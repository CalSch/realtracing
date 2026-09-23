the plan: raytracing but you keep and log all of the info for every ray and every bounce

`structgen.py`:
- takes `structs.h` and generates `structs.glsl` and `structs.py`
- used for synchronizing structs between glsl and python
- and (is going to) take care of padding and such

`theshader.glsl`:
- the main shader that does the math
- it has `#include "structs.h"`, which is processed manually with a regex substitution in `main.py`
- 

## how the tracing works

1. given:
    - there's a list of all the triangles (or a BSP or smth idk that confuses me)
    - there's a list of materials
    - you are a photon
2. choose a starting point
    - idea: choose random triangle weighted by (emission * surface area), then random point on the triangle
        - idk if this will be accurate
3. choose a starting direction
    - usually just random point on the hemisphere facing out from the triangle, but maybe not?
    - could be like `normalize(rand_point_on_sphere() + normal)` or smth
4. cast the ray
5. do the light math
6. repeat
7. visualize

## how 2 run

generate `inputs.bin`: `make structs.py && python3 scenegen.py <obj_file>`
compute the data: `make structs.py && uv run main.py`
look at the data: `make cvis && ./cvis`
