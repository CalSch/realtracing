
#include "structs.glsl"

float ray_triangle(vec3 rayOrigin, vec3 rayDir, vec3 v0, vec3 v1, vec3 v2, float epsilon) {
    vec3 e1 = v1 - v0;
    vec3 e2 = v2 - v0;
    vec3 pvec = cross(rayDir, e2);
    float det = dot(e1, pvec);

    if(abs(det) < epsilon)
        return infinity;

    float invDet = 1.0 / det;
    vec3 tvec = rayOrigin - v0;

    float u = invDet * dot(tvec, pvec);
    if(u < 0.0 || u > 1.0)
        return infinity;

    vec3 qvec = cross(tvec, e1);
    float v = invDet * dot(rayDir, qvec);

    if(v < 0.0 || u + v > 1.0)
        return infinity;

    return dot(e2, qvec) * invDet;
}

float ray_triangle(Ray r, Triangle t) {
    return ray_triangle(r.origin, r.dir, t.p0, t.p1, t.p2, 1e-6);
}

Triangle flip_tri(Triangle t) {
    return Triangle(t.p0, t.p2, t.p1);
}

Hit cast_ray(Ray r, Scene s) {
    Hit closest;
    closest.did_hit = false;
    closest.dist = infinity;
    closest.tri_idx = 0;
    closest.ray = r;

    for (uint i=0;i<s.tri_count;i++) {
        float dist = ray_triangle(r, s.tris[i]);
        if (dist > 0 && dist < closest.dist) {
            closest.did_hit = true;
            closest.dist = dist;
            closest.tri_idx = i;
        }
    }

    closest.pos = r.origin + r.dir * closest.dist;

    return closest;
}

