#version 430
layout(local_size_x = 64) in;

#include "structs.glsl"


struct Particle {
    vec3 pos;
    float mass;
    vec3 vel;
    float pad;
    binky g;
};

layout(std430, binding = 0) buffer ParticleBuffer {
    Particle particles[];
};

void main() {
    uint i = gl_GlobalInvocationID.x;
    if (i >= particles.length()) return;

    particles[i].g.x;

    particles[i].pos = vec3(float(i), float(i) * 2.0, 0.0);
    particles[i].mass = float(i) + 1.0;
    particles[i].vel = vec3(1.0, 0.0, 0.0);
    particles[i].pad = 0.0;
}