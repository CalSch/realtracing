// hey guys i dont normally use ai but i rly didnt want to write smth like this for a one off thing so i made claude do it. im sorry!

// Viewer for huge square grids of int32 stored raw in a file (row-major,
// native-endian). Uses mmap so the 16GiB file is never fully loaded, and
// re-samples only the visible region into a screen-sized texture each time
// the view changes.
//
// Build:
//   gcc gridview.c -O2 -o gridview -I<raylib/src> -L<raylib/src> \
//       -lraylib -lGL -lm -lpthread -ldl -lrt -lX11
//
// Usage:
//   ./gridview <file> <maxval> [palette.txt]
//
//   <file>     path to the raw int32 grid file. Must be N*N*4 bytes for
//              some integer N (N need not be a power of 2, but the file
//              size must be a perfect square times 4).
//   <maxval>   int32 value that maps to the top of the color range.
//              Values are clamped to [0, maxval]. Values < 0 clamp to 0.
//   palette.txt (optional) - a gradient palette file, one "R G B" triplet
//              (0-255 each) per line, at least 2 lines. Value 0 maps to
//              the first line, maxval maps to the last line, linear
//              interpolation between stops. Without this, plain grayscale
//              (0=black, maxval=white) is used.
//
// Controls:
//   Mouse wheel       zoom in/out, centered on the cursor
//   Left-drag / WASD / arrows   pan
//   R                 reset view (fit whole grid)
//   G                 toggle grayscale <-> palette (if palette loaded)
//   Mouse hover        shows grid coords + raw value of the cell under cursor

#include "raylib.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

typedef struct { unsigned char r, g, b; } RGB;

static int32_t *g_map = NULL;      // mmap'd file, int32 per cell
static int64_t  g_n   = 0;         // grid is g_n x g_n
static int64_t  g_maxval = 1;
static RGB     *g_palette = NULL;
static int      g_palette_count = 0;
static int      g_use_palette = 0;

// View state, in grid-space coordinates.
// (view_cx, view_cy) = grid coordinate at the center of the screen
// view_scale = screen pixels per grid cell (can be < 1 when zoomed way out)
static double g_cx, g_cy, g_scale;

static inline int32_t sample_cell(int64_t gx, int64_t gy) {
    if (gx < 0 || gy < 0 || gx >= g_n || gy >= g_n) return 0;
    return g_map[gy * g_n + gx];
}

static inline RGB value_to_color(int32_t v) {
    int64_t vv = v;
    if (vv < 0) vv = 0;
    if (vv > g_maxval) vv = g_maxval;
    double t = (g_maxval > 0) ? (double)vv / (double)g_maxval : 0.0;

    if (g_use_palette && g_palette_count >= 2) {
        double pos = t * (g_palette_count - 1);
        int i0 = (int)pos;
        if (i0 >= g_palette_count - 1) i0 = g_palette_count - 2;
        int i1 = i0 + 1;
        double f = pos - i0;
        RGB a = g_palette[i0], b = g_palette[i1];
        RGB out;
        out.r = (unsigned char)(a.r + (b.r - a.r) * f);
        out.g = (unsigned char)(a.g + (b.g - a.g) * f);
        out.b = (unsigned char)(a.b + (b.b - a.b) * f);
        return out;
    } else {
        unsigned char g = (unsigned char)(t * 255.0);
        RGB out = { g, g, g };
        return out;
    }
}

// Render the current view into an RGBA buffer of size (w,h).
// When zoomed out (scale < 1, i.e. multiple grid cells per pixel), each
// pixel averages a small NxN block of cells for a less noisy picture.
// When zoomed in (scale >= 1), nearest-neighbor upsampling is used.
static void render_view(unsigned char *pixels, int w, int h) {
    double inv_scale = 1.0 / g_scale;
    // top-left grid coordinate visible on screen
    double gx0 = g_cx - (w * 0.5) * inv_scale;
    double gy0 = g_cy - (h * 0.5) * inv_scale;

    if (g_scale >= 1.0) {
        // Zoomed in enough that we can afford per-pixel nearest sampling.
        for (int py = 0; py < h; py++) {
            int64_t gy = (int64_t)floor(gy0 + py * inv_scale);
            unsigned char *row = pixels + (size_t)py * w * 4;
            for (int px = 0; px < w; px++) {
                int64_t gx = (int64_t)floor(gx0 + px * inv_scale);
                RGB c = value_to_color(sample_cell(gx, gy));
                row[px*4+0] = c.r; row[px*4+1] = c.g; row[px*4+2] = c.b; row[px*4+3] = 255;
            }
        }
    } else {
        // Zoomed out: each pixel covers many cells. Average a bounded
        // sub-grid of samples per pixel (cap so it stays fast even when
        // extremely zoomed out over the whole 65536x65536 file).
        double cells_per_px = inv_scale; // >1
        int samples = (int)cells_per_px;
        if (samples > 8) samples = 8;
        if (samples < 1) samples = 1;
        double step = cells_per_px / samples;

        for (int py = 0; py < h; py++) {
            double gy_base = gy0 + py * inv_scale;
            unsigned char *row = pixels + (size_t)py * w * 4;
            for (int px = 0; px < w; px++) {
                double gx_base = gx0 + px * inv_scale;
                long sum = 0; int cnt = 0;
                for (int sy = 0; sy < samples; sy++) {
                    int64_t gy = (int64_t)floor(gy_base + sy * step);
                    for (int sx = 0; sx < samples; sx++) {
                        int64_t gx = (int64_t)floor(gx_base + sx * step);
                        sum += sample_cell(gx, gy);
                        cnt++;
                    }
                }
                int32_t avg = (int32_t)(sum / cnt);
                RGB c = value_to_color(avg);
                row[px*4+0] = c.r; row[px*4+1] = c.g; row[px*4+2] = c.b; row[px*4+3] = 255;
            }
        }
    }
}

static int load_palette(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "warning: could not open palette file %s\n", path); return 0; }
    int cap = 16, n = 0;
    RGB *arr = malloc(sizeof(RGB) * cap);
    int r, g, b;
    while (fscanf(f, "%d %d %d", &r, &g, &b) == 3) {
        if (n >= cap) { cap *= 2; arr = realloc(arr, sizeof(RGB) * cap); }
        arr[n].r = (unsigned char)r; arr[n].g = (unsigned char)g; arr[n].b = (unsigned char)b;
        n++;
    }
    fclose(f);
    if (n < 2) { fprintf(stderr, "warning: palette needs >=2 entries, ignoring\n"); free(arr); return 0; }
    g_palette = arr;
    g_palette_count = n;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s <file> <maxval> [palette.txt]\n", argv[0]);
        return 1;
    }
    const char *path = argv[1];
    g_maxval = atoll(argv[2]);
    if (g_maxval < 1) g_maxval = 1;

    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); return 1; }
    int64_t total_bytes = st.st_size;
    int64_t total_cells = total_bytes / 4;
    if (total_bytes % 4 != 0) {
        fprintf(stderr, "error: file size %lld is not a multiple of 4\n", (long long)total_bytes);
        return 1;
    }
    int64_t n = (int64_t)llround(sqrt((double)total_cells));
    // adjust for rounding error
    while (n * n > total_cells) n--;
    while ((n + 1) * (n + 1) <= total_cells) n++;
    if (n * n != total_cells) {
        fprintf(stderr, "error: file does not contain a perfect square number of int32 cells "
                        "(got %lld cells, nearest square root %lld)\n",
                        (long long)total_cells, (long long)n);
        return 1;
    }
    g_n = n;

    void *m = mmap(NULL, (size_t)total_bytes, PROT_READ, MAP_PRIVATE, fd, 0);
    if (m == MAP_FAILED) { perror("mmap"); return 1; }
    madvise(m, (size_t)total_bytes, MADV_RANDOM);
    g_map = (int32_t *)m;
    close(fd);

    if (argc >= 4) {
        if (load_palette(argv[3])) g_use_palette = 1;
    }

    printf("Loaded %s: grid %lld x %lld, maxval=%lld%s\n",
           path, (long long)g_n, (long long)g_n, (long long)g_maxval,
           g_use_palette ? " (palette loaded)" : " (grayscale)");

    const int win_w = 1200, win_h = 900;
    SetConfigFlags(FLAG_WINDOW_RESIZABLE);
    InitWindow(win_w, win_h, "Grid Viewer");
    SetTargetFPS(60);

    // initial view: fit whole grid on screen
    g_cx = g_n / 2.0;
    g_cy = g_n / 2.0;
    g_scale = (double)win_w / (double)g_n;
    if ((double)win_h / g_n < g_scale) g_scale = (double)win_h / g_n;

    int tex_w = win_w, tex_h = win_h;
    Image img = GenImageColor(tex_w, tex_h, BLANK);
    Texture2D tex = LoadTextureFromImage(img);
    unsigned char *pixels = malloc((size_t)tex_w * tex_h * 4);

    int dirty = 1;
    bool dragging = false;
    Vector2 dragStart = {0,0};
    double dragStartCx = 0, dragStartCy = 0;

    while (!WindowShouldClose()) {
        int cw = GetScreenWidth(), ch = GetScreenHeight();
        if (cw != tex_w || ch != tex_h) {
            tex_w = cw; tex_h = ch;
            UnloadTexture(tex);
            UnloadImage(img);
            free(pixels);
            img = GenImageColor(tex_w, tex_h, BLANK);
            tex = LoadTextureFromImage(img);
            pixels = malloc((size_t)tex_w * tex_h * 4);
            dirty = 1;
        }

        // --- input ---
        float wheel = GetMouseWheelMove();
        if (wheel != 0) {
            Vector2 mp = GetMousePosition();
            double before_gx = g_cx + (mp.x - tex_w * 0.5) / g_scale;
            double before_gy = g_cy + (mp.y - tex_h * 0.5) / g_scale;
            double zoom = pow(1.2, wheel);
            g_scale *= zoom;
            // clamp scale: don't zoom out past ~whole grid visible, don't
            // zoom in past 1 cell = 4096 px
            double min_scale = fmin((double)tex_w, (double)tex_h) / (double)g_n * 0.5;
            if (g_scale < min_scale) g_scale = min_scale;
            if (g_scale > 4096.0) g_scale = 4096.0;
            double after_gx = g_cx + (mp.x - tex_w * 0.5) / g_scale;
            double after_gy = g_cy + (mp.y - tex_h * 0.5) / g_scale;
            g_cx += (before_gx - after_gx);
            g_cy += (before_gy - after_gy);
            dirty = 1;
        }

        if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            dragging = true;
            dragStart = GetMousePosition();
            dragStartCx = g_cx; dragStartCy = g_cy;
        }
        if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT)) dragging = false;
        if (dragging) {
            Vector2 mp = GetMousePosition();
            double dx = (mp.x - dragStart.x) / g_scale;
            double dy = (mp.y - dragStart.y) / g_scale;
            double newcx = dragStartCx - dx;
            double newcy = dragStartCy - dy;
            if (newcx != g_cx || newcy != g_cy) dirty = 1;
            g_cx = newcx; g_cy = newcy;
        }

        double keypan = (200.0 / g_scale) * GetFrameTime();
        if (IsKeyDown(KEY_LEFT)  || IsKeyDown(KEY_A)) { g_cx -= keypan; dirty = 1; }
        if (IsKeyDown(KEY_RIGHT) || IsKeyDown(KEY_D)) { g_cx += keypan; dirty = 1; }
        if (IsKeyDown(KEY_UP)    || IsKeyDown(KEY_W)) { g_cy -= keypan; dirty = 1; }
        if (IsKeyDown(KEY_DOWN)  || IsKeyDown(KEY_S)) { g_cy += keypan; dirty = 1; }

        if (IsKeyPressed(KEY_R)) {
            g_cx = g_n / 2.0; g_cy = g_n / 2.0;
            g_scale = (double)tex_w / (double)g_n;
            if ((double)tex_h / g_n < g_scale) g_scale = (double)tex_h / g_n;
            dirty = 1;
        }
        if (IsKeyPressed(KEY_G) && g_palette_count >= 2) {
            g_use_palette = !g_use_palette;
            dirty = 1;
        }

        // clamp center so we don't pan off into empty space forever
        if (g_cx < 0) g_cx = 0;
        if (g_cy < 0) g_cy = 0;
        if (g_cx > g_n) g_cx = g_n;
        if (g_cy > g_n) g_cy = g_n;

        if (dirty) {
            render_view(pixels, tex_w, tex_h);
            UpdateTexture(tex, pixels);
            dirty = 0;
        }

        Vector2 mp = GetMousePosition();
        int64_t hover_gx = (int64_t)floor(g_cx + (mp.x - tex_w * 0.5) / g_scale);
        int64_t hover_gy = (int64_t)floor(g_cy + (mp.y - tex_h * 0.5) / g_scale);
        int32_t hover_val = sample_cell(hover_gx, hover_gy);

        BeginDrawing();
        ClearBackground(BLACK);
        DrawTexture(tex, 0, 0, WHITE);

        DrawRectangle(0, 0, tex_w, 30, Fade(BLACK, 0.6f));
        DrawText(TextFormat("grid %lldx%ld  scale=%.4f px/cell  center=(%.0f,%.0f)  cell=(%lld,%lld) val=%d  [wheel=zoom drag/WASD=pan R=reset G=palette]",
                            (long long)g_n, (long)g_n, g_scale, g_cx, g_cy,
                            (long long)hover_gx, (long long)hover_gy, hover_val),
                 8, 8, 14, RAYWHITE);

        EndDrawing();
    }

    UnloadTexture(tex);
    UnloadImage(img);
    free(pixels);
    if (g_palette) free(g_palette);
    munmap(g_map, (size_t)total_bytes);
    CloseWindow();
    return 0;
}