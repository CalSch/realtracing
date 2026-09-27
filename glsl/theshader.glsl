#version 430

const float infinity = 1.0 / 0.0;

#include "structs.glsl"
#include "random.glsl"

layout(std430, binding = 0) buffer ResultBuffer {
    Result results[];
};
layout(std430, binding = 1) buffer InputBuffer {
    Scene scene;
};
layout(std430, binding = 2) buffer TriangleBuffer {
    Triangle triangles[];
};
layout(std430, binding = 3) buffer BVHBuffer {
    BVHNode bvh_nodes[];
};

#include "math.glsl"

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
        vec3(0,1,0),
        // random3_s()*1.0,
        random_dir()
        // normalize(random_dir()+vec3(-8,15,-8))
        // normalize(vec3(1,2,3) + random_dir()*0.005 )
    );
    // Ray ray = Ray(
    //     vec3(random_s()*5.0,random_s()*5.0,0),
    //     normalize(vec3(0,0,1))
    // );

    Hit h;
    h.did_hit = true;

    vec3 ray_color = vec3(1,1,1);

    for (int i=0; i<MAX_BOUNCES; i++) {
        h = cast_ray(ray);

        if (random_u() < 0.0)
            h.did_hit = false;

        res.bounces[i] = h;
        res.last_ray = ray;

        vec3 specular_dir = reflect(ray.dir,h.normal);
        vec3 diffuse_dir = normalize(random_dir() + h.normal);
        bool is_diffuse = random_u()<0.5;
        vec3 new_dir = mix(specular_dir, diffuse_dir, is_diffuse?1:0);

        ray = Ray(
            h.pos,
            new_dir
        );

        ray.origin += ray.dir * 0.001;
        res.last_ray2 = ray;


        if (!h.did_hit)
            break;
    }


    results[gl_GlobalInvocationID.x] = res;
    // results[0].idx = int(idx);


    
}