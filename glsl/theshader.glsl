#version 430

#include "structs.glsl"
#include "random.glsl"

layout(std430, binding = 1) buffer InputBuffer {
    Input input_data;
};
layout(std430, binding = 0) buffer ResultBuffer {
    Result results[];
};

uniform uint start_idx = 0;

void main() {

    if (gl_GlobalInvocationID.x >= results.length()) {
        return;
    }


    uint idx = gl_GlobalInvocationID.x + start_idx;

    rng_seed = randomS(idx+1);

    Result r;

    r.id = int(idx);

    // r.ray.dir.x = float(start_idx);
    // r.ray.origin = random3();
    r.ray.origin = vec3(0,0,0);
    r.ray.dir = random_dir();
    // r.ray.dir = random;

    results[gl_GlobalInvocationID.x] = r;
    // results[0].idx = int(idx);


    
}