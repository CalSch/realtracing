#include "structs.h"
#include <stdio.h>
#include <stdlib.h>
#include <raylib.h>
#include <raymath.h>

#define LOGd(val) printf(#val " = %d\n", val)


Vector3 conv_vec3(s_vec3 v) {return (Vector3){-v.x,v.y,v.z};} // do -x bc raylib is right-handed (gross)

int main() {
    printf("hello wold!\n");
    FILE* f = fopen("results.bin","rb");

    if (f == NULL) {
        perror("open() results.bin");
        return 1;
    }

    fseek(f, 0, SEEK_END);
    size_t file_size = ftell(f);
    rewind(f);

    size_t result_count = file_size / sizeof(s_Result);        
    LOGd(file_size);
    LOGd(sizeof(s_Result));
    LOGd(result_count);
    LOGd(result_count*sizeof(s_Result) - file_size);

    // allocate space for the data
    s_Result* results = calloc(result_count, sizeof(s_Result));

    // read in the data
    fread(results, sizeof(s_Result), result_count, f);

    fclose(f);

    // for (int i=0;i<result_count;i++) {
    //     printf("res[%d].ray.orig.x = %f\n", i, results[i].hit.ray.dir.x);
    // }



    InitWindow(1270,720,"gump!");

    DisableCursor();

    Camera3D cam = (Camera3D){(Vector3){8,8,8},(Vector3){0,0,0},(Vector3){0,1,0},.fovy=60};

    while (!WindowShouldClose()) {

        // UpdateCamera(&cam, CAMERA_ORBITAL);
        UpdateCamera(&cam, CAMERA_FREE);

        BeginDrawing();
        ClearBackground(DARKBLUE);

        BeginMode3D(cam);

        DrawGrid(10,1);

        for (int i=0;i<result_count;i++) {
            s_Result r = results[i];

            if (!r.hit.did_hit)
                continue;

            Vector3 orig = conv_vec3(r.hit.ray.origin);
            Vector3 dir = conv_vec3(r.hit.ray.dir);

            Vector3 hit = Vector3Add(orig, Vector3Scale(dir, r.hit.dist));

            // SetRandomSeed(r.hit.tri_idx);
            // Color c = ColorFromHSV(GetRandomValue(0,360),1,1);
            Color c = RED;

            // DrawLine3D(orig, hit, WHITE);
            DrawCube(hit,0.05,0.05,0.05,c);
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