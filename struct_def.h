#include "glsl_include.h"

#define MAX_ITERS 256
#define MAX_TRIANGLES 4


struct Triangle {
    vec3 p0;
    vec3 p1;
    vec3 p2;
};

struct Ray {
    vec3 origin;
    vec3 dir;
};

struct Scene {
    Triangle tris[MAX_TRIANGLES];
    uint tri_count;
};

struct Hit {
    bool did_hit;
    Ray ray;
    float dist;
    uint tri_idx;
};

struct Result {
    int id;
    Hit hit;
};

struct Input {
    Scene scene;
};