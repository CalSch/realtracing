#version 430
layout(local_size_x = 64) in;

#include "structs.glsl"


struct Particle {
    vec3 pos;
    float mass;
    vec3 vel;
    float pad;
    // binky g;
};

layout(std430, binding = 0) buffer ResultBuffer {
    result results[];
};

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= results.length()) return;

    results[i].bounce_count = 4;
}