#version 430

#include "structs.glsl"

layout(std430, binding = 1) buffer InputBuffer {
    Input input_data;
};
layout(std430, binding = 0) buffer ResultBuffer {
    Result results[];
};

uniform uint start_idx;

vec2 c_mul(vec2 a, vec2 b) {
    return vec2(
        a.x*b.x - a.y*b.y,
        a.x*b.y + a.y*b.x
    );
}

vec2 do_iter(vec2 z, vec2 c) {
    return c_mul(z,z) + c;
}

void main() {
    uint idx = gl_GlobalInvocationID.x + start_idx;
    if (idx >= results.length()) {
        return;
    }

    ivec2 coord = ivec2(
        idx % input_data.resolution.x,
        idx / input_data.resolution.x
    );
    vec2 uv = vec2(coord) / vec2(input_data.resolution);

    Result r;
    r.idx = int(idx);

    r.c.x = mix(input_data.win_min.x, input_data.win_max.x, uv.x);
    r.c.y = mix(input_data.win_min.y, input_data.win_max.y, uv.y);

    vec2 z = vec2(0,0);

    for (int i=0;i<MAX_ITERS;i++) {
        z = do_iter(z, r.c);
        r.iters[i] = z;
        if (length(z) > 2.0) {
            r.time_to_escape = i;
            break;
        }
    }

    results[idx] = r;
    // results[0].idx = int(idx);


    
}