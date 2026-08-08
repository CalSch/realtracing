#include "glsl_include.h"

#define MAX_ITERS 256

struct Result {
    // int idx;
    int time_to_escape;
    // vec2 c;
    // vec2 iters[MAX_ITERS];
};

struct Input {
    ivec2 resolution;
    vec2 win_min;
    vec2 win_max;
};