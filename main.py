import moderngl
import numpy as np
import re
import structs

# --- GLSL struct (std430 layout rules) ---
# struct Particle {
#     vec3 pos;   // occupies 16 bytes (vec3 aligns to 16, not 12)
#     float mass; // fills the 4 bytes left in that 16-byte slot
#     vec3 vel;   // another 16 bytes
#     float pad;  // explicit padding to make the struct size a multiple of 16
# };
# Total size: 32 bytes per struct

COMPUTE_SHADER = open("theshader.glsl",'r').read()

COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", lambda m: open(m.group(1),'r').read(), COMPUTE_SHADER)

# print(COMPUTE_SHADER)

# --- Matching numpy dtype (must mirror std430 padding exactly) ---
particle_dtype = np.dtype([
    ("pos", np.float32, 3),
    ("mass", np.float32),
    ("vel", np.float32, 3),
    ("pad", np.float32),
])  # itemsize == 32, matches GLSL struct size

N = 256

ctx = moderngl.create_standalone_context(require=430)

compute = ctx.compute_shader(COMPUTE_SHADER)

# allocate buffer sized for N structs, zero-initialized
init_data = np.zeros(N, dtype=structs.dtype_result)
buffer = ctx.buffer(init_data.tobytes())
buffer.bind_to_storage_buffer(0)

# dispatch: local_size_x=64, so N/64 work groups
compute.run(group_x=N // 64)

# read back and reinterpret as the same struct array
result = np.frombuffer(buffer.read(), dtype=structs.dtype_result)

print(result[:5])
print("dtype itemsize:", structs.dtype_result.itemsize)