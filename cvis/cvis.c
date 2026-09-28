#include "../structs.h"
#include <stdio.h>
#include <stdlib.h>
#include <raylib.h>
#include <raymath.h>
#include <rlgl.h>

#define LOGd(val) printf(#val " = %d\n", val)
#define LOGfmt(val,fmt) printf(#val " = " fmt "\n", val)


Vector3 conv_vec3(s_vec3 v) {return (Vector3){v.x,v.y,v.z};} // do -x bc raylib is right-handed (gross)

Color color_hash(int i, float sat, float value) {
    SetRandomSeed((i+412)*19);
    Color c = ColorFromHSV(GetRandomValue(0,360), sat, value);
    return c;
}

s_Result* results = NULL;
size_t result_count = 0;
s_Input input;

Mesh point_mesh;
Shader point_shader;
Material point_material;
float point_size = 0.003;

int hit_point_count = 0;
Matrix* hit_point_transforms = NULL;
Vector4* hit_point_colors = NULL;

Shader triangle_shader;
Material triangle_material;



void load_results() {
    {
        FILE* f = fopen("results.bin","rb");

        if (f == NULL) {
            perror("open() results.bin");
            exit(1);
        }

        fseek(f, 0, SEEK_END);
        size_t file_size = ftell(f);
        rewind(f);

        result_count = file_size / sizeof(s_Result);
        LOGd(file_size);
        LOGd(sizeof(s_Result));
        LOGd(result_count);
        LOGd(result_count*sizeof(s_Result) - file_size);

        // allocate space for the data
        results = calloc(result_count, sizeof(s_Result));

        // read in the data
        fread(results, sizeof(s_Result), result_count, f);

        fclose(f);
    }

    {
        FILE* f = fopen("inputs.bin","rb");

        if (f == NULL) {
            perror("open() inputs.bin");
            exit(1);
        }

        fseek(f, 0, SEEK_END);
        size_t file_size = ftell(f);
        rewind(f);

        printf("these should match:\n");
        LOGd(file_size);
        LOGd(sizeof(input));

        fread(&input, sizeof(input), 1, f);

        fclose(f);
    }
}




void calc_hit_point_transforms(int res_count, s_Result* results) {
    printf("\ngenerating hit point transforms...\n");
    hit_point_count = res_count*MAX_BOUNCES;

    hit_point_transforms = calloc(hit_point_count,sizeof(Matrix));
    hit_point_colors = calloc(hit_point_count,sizeof(Vector4));

    LOGd(hit_point_count);
    printf("transforms take up %d MiB\n", hit_point_count*sizeof(Matrix)/1024/1024);
    printf("color      take up %d MiB\n", hit_point_count*sizeof(Vector4)/1024/1024);

    // Matrix default_matrix = MatrixScale(point_size,point_size,point_size);

    for (int i=0;i<res_count;i++) {
        s_Result r = results[i];

        for (int j=0;j<MAX_BOUNCES;j++) {
            s_Hit h = r.bounces[j];

            int idx = i*MAX_BOUNCES + j;

            if (!h.did_hit) {
                break;
            } else {
                Vector3 p = conv_vec3(h.pos);
                s_vec3 c = h.ray_color;
                // hit_point_transforms[idx] = MatrixMultiply(MatrixScale(point_size,point_size,point_size), MatrixTranslate(p.x,p.y,p.z));
                hit_point_transforms[idx].m0 = p.x,
                hit_point_transforms[idx].m1 = p.y,
                hit_point_transforms[idx].m2 = p.z,
                // hit_point_transforms[idx].m3 = p.z,
                hit_point_transforms[idx].m4 = c.x;
                hit_point_transforms[idx].m5 = c.y;
                hit_point_transforms[idx].m6 = c.z;
            }

        }
    }

    int unused_count = 0;
    for (int i=0;i<hit_point_count;i++) {
        if (hit_point_transforms[i].m15 == 0)
            unused_count++;
    }
    LOGd(unused_count);
    printf("%d unused / %d total = %2.4f%% unused\n", unused_count, hit_point_count, 100.0*(float)unused_count/(float)hit_point_count);

    if (0) {
        Matrix M=hit_point_transforms[0];
        for (int row=0;row<4;row++) {
            for (int col=0;col<4;col++)
                printf("%+f ",MatrixToFloat(M)[col*4+row]);
            printf("\n");
        }
    }

    printf("done!\n\n");
}

void draw_scene() {
    BeginShaderMode(triangle_shader);
    for (int i=0;i<input.scene.tri_count;i++) {
        s_Triangle t = input.triangles[i];
        // printf("triangle: %f %f %f\n",t.p0.x,t.p0.y,t.p0.z);
        DrawTriangle3D(
            conv_vec3(t.p0),
            conv_vec3(t.p1),
            conv_vec3(t.p2),
            color_hash(i, 0.9, 0.6)
        );
    }
    EndShaderMode();
}

void draw_hit_points() {
    DrawMeshInstanced(point_mesh, point_material, hit_point_transforms, hit_point_count);
}

int main() {
    printf("hello wold!\n");


    // for (int i=0;i<result_count;i++) {
    //     printf("res[%d].ray.orig.x = %f\n", i, results[i].hit.ray.dir.x);
    // }



    SetTraceLogLevel(LOG_WARNING);
    SetConfigFlags(FLAG_MSAA_4X_HINT);
    InitWindow(1270,720,"gump!");

    double load_start_time = GetTime();
    {
        BeginDrawing();
        ClearBackground(BLACK);
        DrawText("loading...",10,10,30,WHITE);
        EndDrawing();
    }

    load_results();
    calc_hit_point_transforms(result_count,results);


    DisableCursor();

    Camera3D cam = (Camera3D){(Vector3){2,2,0},(Vector3){0,0,0},(Vector3){0,1,0},.fovy=60};

    // point_mesh = GenMeshCube(1,1,1);
    point_mesh = GenMeshPoly(4,1);
    point_shader = LoadShader("cvis/point.vs","cvis/point.fs");
    point_material = LoadMaterialDefault();
    point_material.shader=point_shader;

    triangle_material = LoadMaterialDefault();
    triangle_shader = LoadShader("cvis/tri.vs","cvis/tri.fs");
    triangle_material.shader = triangle_shader;

    rlDisableBackfaceCulling();


    double load_end_time = GetTime();
    printf("Load took %f ms\n",1000.0*(load_end_time-load_start_time));
    {
        BeginDrawing();
        ClearBackground(WHITE);
        DrawText("loaded!",10,10,30,BLACK);
        EndDrawing();
    }


    while (!WindowShouldClose()) {

        if (IsKeyDown(KEY_LEFT_BRACKET))
            cam.fovy *= 1.0+(1.0 / (float)GetFPS());
        if (IsKeyDown(KEY_RIGHT_BRACKET))
            cam.fovy /= 1.0+(1.0 / (float)GetFPS());

        if (IsKeyPressed(KEY_F1)) {
            printf("taking a screenshot\n");
            // TakeScreenshot("screenshot.png");
            char path_buf[256];
            for (int i=0;i<=999;i++) {
                sprintf(path_buf,"stuff/%03d.png",i);
                if (!FileExists(path_buf)) {
                    printf("saving to %s\n",path_buf);
                    TakeScreenshot(path_buf);
                    break;
                }
            }
        }

        // printf("time = %f frame = %f\n",GetTime(),GetFrameTime());

        // UpdateCamera(&cam, CAMERA_ORBITAL);
        UpdateCamera(&cam, CAMERA_FREE);

        BeginDrawing();
        ClearBackground(DARKBLUE);

        BeginMode3D(cam);

        DrawGrid(10,1);

        // draw_scene();

        // if (0)
        for (int i=0;i<result_count;i++) {
            s_Result r = results[i];

            s_Hit last_hit;
            for (int j=0;j<MAX_BOUNCES;j++) {
                s_Hit h = r.bounces[j];

                if (!h.did_hit)
                    break;
                
                last_hit = h;

                Vector3 orig = conv_vec3(h.ray.origin);

                Vector3 hit = conv_vec3(h.pos);

                // Color c = color_hash(h.tri_idx, 0.9);

                // DrawLine3D(orig, hit, WHITE);
                // DrawLine3D(hit,Vector3Add(hit,Vector3Scale(conv_vec3(h.normal),0.25)),MAGENTA);
                // DrawCube(hit,0.01,0.01,0.01,WHITE);
            }
            // printf("%f\n", r.last_ray2.dir.x);
            // DrawRay((Ray){.position=conv_vec3(r.last_ray.origin), .direction=conv_vec3(r.last_ray.dir)}, RED);
            // DrawRay((Ray){.position=conv_vec3(last_hit.pos), .direction=conv_vec3(r.last_ray2.dir)}, GREEN);

        }
        
        draw_hit_points();

        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){1,0,0}),RED);
        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){0,1,0}),GREEN);
        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){0,0,1}),BLUE);

        EndMode3D();

        DrawFPS(10,10);

        EndDrawing();

    }

    CloseWindow();
}