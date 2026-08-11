#include "glsl_include.h"

#define MAX_ITERS 256

struct Camera {
    vec3 origin;
    vec3 front;
    vec3 right;
    float fov;
};

struct Ray {
    vec3 origin;
    vec3 dir;
};

struct Result {
    int id;
    Ray ray;
};

struct Input {
    Camera cam;
};