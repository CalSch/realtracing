#include "glsl_include.h"

#define MAX_BOUNCES 4

struct bounce {
    vec3 hit_point;
    float pad1;
    vec3 incoming;
    float pad2;
    vec3 normal;
    float pad3;
};

struct result {
    int bounce_count;
    int pad;
    int pad3;
    int pad4;
    vec3 init;
    float pad2;
    bounce bounces[MAX_BOUNCES];
};