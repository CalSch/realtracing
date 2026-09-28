#include "glsl_include.h"

#define MAX_BOUNCES 6
#define MAX_TRIANGLES 10000
#define MAX_BVH_NODES MAX_TRIANGLES
#define MAX_MATERIALS 8


struct Triangle {
    vec3 p0;
    vec3 p1;
    vec3 p2;
    int material_idx;
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

struct Material {
    vec3 c_diffuse;
};

struct Scene {
    uint tri_count;
    Material materials[MAX_MATERIALS];
};

struct Hit {
    bool did_hit;
    Ray ray;
    float dist;
    vec3 pos;
    vec3 normal;
    uint tri_idx;

    vec3 ray_color;
};

struct Result {
    int id;
    Hit bounces[MAX_BOUNCES];
};

struct Input {
    Scene scene;
    Triangle triangles[MAX_TRIANGLES];
    BVHNode bvh_nodes[MAX_BVH_NODES];
};