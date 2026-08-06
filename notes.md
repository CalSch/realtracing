the plan: raytracing but you keep and log all of the info for every ray and every bounce

`structgen.py`:
- takes `structs.h` and generates `structs.glsl` and `structs.py`
- used for synchronizing structs between glsl and python
- and (is going to) take care of padding and such

`theshader.glsl`:
- the main shader that does the math
- it has `#include "structs.h"`, which is processed manually with a regex substitution in `main.py`
- 