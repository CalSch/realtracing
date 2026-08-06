from CStructParser.CStructParser import CStructParser, StructField
import pprint
import sys

# Initialize parser with structure definition
parser = CStructParser(sys.stdin.read(), endian='little', debug=True)

fields: dict[str, dict[str, StructField]] = parser.struct_fields

# --- std430 base alignment/size table (bytes) ---
# type_name -> (size, alignment)
KNOWN_TYPES = {
    "float": (4, 4), "int": (4, 4), "uint": (4, 4), "bool": (4, 4),
    "double": (8, 8),
    "vec2": (8, 8), "ivec2": (8, 8), "uvec2": (8, 8),
    "vec3": (12, 16), "ivec3": (12, 16), "uvec3": (12, 16),
    "vec4": (16, 16), "ivec4": (16, 16), "uvec4": (16, 16),
    "mat3": (48, 16), "mat4": (64, 16),
}

PY_TYPE_LUT = {
    "float": "np.float32",
    "int": "np.int32",
    "uint": "np.uint32",
    "bool": "np.int32",
    "double": "np.float64",
}


def align_up(n, a):
    return ((n + a - 1) // a) * a


py = "import numpy as np\n\n"
glsl = ""

for struct_name in fields:
    struct = fields[struct_name]

    # vec2/vec3/vec4 etc are GLSL builtins -- skip emitting a glsl struct,
    # and don't recompute their alignment (it's hardcoded above, since it
    # can't be derived from their member floats: e.g. vec3's 3 floats sum
    # to align 4, but GLSL still aligns vec3 itself to 16).
    glsl_skip = struct_name in KNOWN_TYPES

    if not glsl_skip:
        glsl += f"struct {struct_name} {{\n"
    py += f"dtype_{struct_name} = np.dtype([\n"

    offset = 0
    max_align = 4
    pad_idx = 0

    for field in struct:
        val = struct[field]

        elem_size, elem_align = KNOWN_TYPES[val.type_name]

        if val.array_size is not None:
            # std430 array stride = element rounded up to its own alignment
            # (e.g. float[] stride=4 tightly packed, vec3[] stride=16)
            field_size = align_up(elem_size, elem_align) * val.array_size
            field_align = elem_align
        else:
            # non-array fields consume only their REAL size, not size
            # rounded up to alignment -- this is what allows a trailing
            # scalar to pack into a vec3's leftover 4 bytes (only the
            # *next* field's offset gets rounded up, absorbing the gap)
            field_size = elem_size
            field_align = elem_align

        if not glsl_skip:
            # only compute/insert padding for user-defined structs;
            # builtins (vec2/3/4) are already tightly packed and correct.
            aligned_offset = align_up(offset, field_align)
            gap = aligned_offset - offset
            if gap > 0:
                py += f"\t('_pad{pad_idx}', np.uint8, {gap}),\n"
                pad_idx += 1
                offset = aligned_offset
            max_align = max(max_align, field_align)

        glsl_array = f"[{val.array_size}]" if val.array_size is not None else ""
        py_type = PY_TYPE_LUT.get(val.type_name, f"dtype_{val.type_name}")
        py_array = f", {val.array_size}" if val.array_size is not None else ""

        if not glsl_skip:
            glsl += f"\t{val.type_name} {val.name}{glsl_array};\n"
        py += f"\t('{val.name}', {py_type}{py_array}),\n"

        offset += field_size

    if not glsl_skip:
        struct_align = align_up(max_align, 16)
        final_size = align_up(offset, 16)
        trailing_gap = final_size - offset
        if trailing_gap > 0:
            py += f"\t('_pad{pad_idx}', np.uint8, {trailing_gap}),\n"
        KNOWN_TYPES[struct_name] = (final_size, struct_align)
        glsl += "};\n"

    py += "])\n"

with open("structs.glsl", 'w') as f:
    f.write(glsl)
with open("structs.py", 'w') as f:
    f.write(py)