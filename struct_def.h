#include "glsl_include.h"

#define MAX_BOUNCES 2
#define MAX_TRIANGLES 80000
#define MAX_BVH_NODES MAX_TRIANGLES


struct Triangle {
    vec3 p0;
    vec3 p1;
    vec3 p2;
};

struct Ray {
    vec3 origin;
    vec3 dir;
};

struct AABB {
    vec3 min;
    vec3 max;
};

struct BVHNode {
    AABB bounds;
    uint childA;
    uint childB;
    uint tri_start_idx;
    uint tri_count;
};

struct Scene {
    uint tri_count;
};

struct Hit {
    bool did_hit;
    Ray ray;
    float dist;
    vec3 pos;
    vec3 normal;
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
    Triangle triangles[MAX_TRIANGLES];
    BVHNode bvh_nodes[MAX_BVH_NODES];
};