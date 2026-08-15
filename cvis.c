#include "structs.h"
#include <stdio.h>
#include <stdlib.h>
#include <raylib.h>
#include <raymath.h>

#define LOGd(val) printf(#val " = %d\n", val)


Vector3 conv_vec3(s_vec3 v) {return (Vector3){-v.x,v.y,v.z};} // do -x bc raylib is right-handed (gross)

Color color_hash(int i, float value) {
    SetRandomSeed((i+412)*19);
    Color c = ColorFromHSV(GetRandomValue(0,360), 1, value);
    return c;
}

int main() {
    printf("hello wold!\n");

    s_Result* results = NULL;
    size_t result_count = 0;
    {
        FILE* f = fopen("results.bin","rb");

        if (f == NULL) {
            perror("open() results.bin");
            return 1;
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

    s_Input input;
    {
        FILE* f = fopen("inputs.bin","rb");

        if (f == NULL) {
            perror("open() inputs.bin");
            return 1;
        }

        fseek(f, 0, SEEK_END);
        size_t file_size = ftell(f);
        rewind(f);

        printf("these should match:\n");
        LOGd(file_size);
        LOGd(sizeof(s_Input));

        fread(&input, sizeof(input), 1, f);

        fclose(f);
    }

    // for (int i=0;i<result_count;i++) {
    //     printf("res[%d].ray.orig.x = %f\n", i, results[i].hit.ray.dir.x);
    // }



    SetTraceLogLevel(LOG_WARNING);
    InitWindow(1270,720,"gump!");

    DisableCursor();

    Camera3D cam = (Camera3D){(Vector3){2,2,0},(Vector3){0,0,0},(Vector3){0,1,0},.fovy=60};

    while (!WindowShouldClose()) {

        // printf("time = %f frame = %f\n",GetTime(),GetFrameTime());

        // UpdateCamera(&cam, CAMERA_ORBITAL);
        UpdateCamera(&cam, CAMERA_FREE);

        BeginDrawing();
        ClearBackground(DARKBLUE);

        BeginMode3D(cam);

        DrawGrid(10,1);

        for (int i=0;i<input.scene.tri_count;i++) {
            s_Triangle t = input.scene.tris[i];
            DrawTriangle3D(
                conv_vec3(t.p0),
                conv_vec3(t.p1),
                conv_vec3(t.p2),
                color_hash(i, 0.7)
            );
            DrawTriangle3D(
                conv_vec3(t.p1),
                conv_vec3(t.p0),
                conv_vec3(t.p2),
                color_hash(i, 0.4)
            );
        }

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

                Color c = color_hash(h.tri_idx, 0.9);

                DrawLine3D(orig, hit, WHITE);
                DrawCube(hit,0.02,0.02,0.02,c);
            }
            printf("%f\n", r.last_ray2.dir.x);
            // DrawRay((Ray){.position=conv_vec3(r.last_ray.origin), .direction=conv_vec3(r.last_ray.dir)}, RED);
            // DrawRay((Ray){.position=conv_vec3(last_hit.pos), .direction=conv_vec3(r.last_ray2.dir)}, GREEN);

        }

        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){1,0,0}),RED);
        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){0,1,0}),GREEN);
        DrawLine3D((Vector3){0,0,0},conv_vec3((s_vec3){0,0,1}),BLUE);

        EndMode3D();

        DrawFPS(10,10);

        EndDrawing();

    }

    CloseWindow();
}