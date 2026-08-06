#include "glsl_include.h"

#define MAX_BOUNCES 4

struct bounce {
    vec3 hit_point;
    vec3 incoming;
    vec3 normal;
};

struct result {
    vec3 init;
    int bounce_count;
    bounce bounces[MAX_BOUNCES];
};