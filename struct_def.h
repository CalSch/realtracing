#include "glsl_include.h"

#define MAX_BOUNCES 800
#define MAX_TRIANGLES 256


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
    vec3 pos;
    uint tri_idx;
};

struct Result {
    int id;
    Hit bounces[MAX_BOUNCES];
    Ray last_ray;
    Ray last_ray2;
};

struct Input {
    Scene scene;
};