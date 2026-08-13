#version 430

const float infinity = 1.0 / 0.0;

#include "structs.glsl"
#include "random.glsl"
#include "math.glsl"

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

    rng_seed = randomSeeded(idx+1);

    Result res;

    res.id = int(idx);

    Ray ray = Ray(
        vec3(0,0,0),
        random_dir()
    );
    // Ray ray = Ray(
    //     vec3(random_s()*5.0,random_s()*5.0,0),
    //     normalize(vec3(0,0,1))
    // );

    res.hit = cast_ray(ray, input_data.scene);


    results[gl_GlobalInvocationID.x] = res;
    // results[0].idx = int(idx);


    
}