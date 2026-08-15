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
uniform uint seed = 0;

void main() {

    if (gl_GlobalInvocationID.x >= results.length()) {
        return;
    }


    uint idx = gl_GlobalInvocationID.x + start_idx;

    rng_seed = randomSeeded(idx+1+seed);

    Result res;

    res.id = int(idx);

    Ray ray = Ray(
        vec3(0,0,0),
        // random3_s()*1.0,
        // random_dir()
        normalize(random3_s()*vec3(1,1,1)+vec3(0,0,4))
    );
    // Ray ray = Ray(
    //     vec3(random_s()*5.0,random_s()*5.0,0),
    //     normalize(vec3(0,0,1))
    // );

    for (int i=0;i<MAX_BOUNCES;i++) {
        Hit h = cast_ray(ray, input_data.scene);
        Triangle t = input_data.scene.tris[h.tri_idx];
        vec3 t_norm = normalize(cross(t.p1-t.p0, t.p2-t.p0));
        res.bounces[i] = h;
        res.last_ray = ray;
        ray = Ray(
            h.pos,
            reflect(ray.dir,t_norm)
            // normalize(random_dir()+t_norm)
        );
        ray.origin += ray.dir * 0.001;
        res.last_ray2 = ray;
        if (!h.did_hit)
            break;
    }


    results[gl_GlobalInvocationID.x] = res;
    // results[0].idx = int(idx);


    
}