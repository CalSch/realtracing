from CStructParser.CStructParser import CStructParser, StructField
import pprint
import sys
import re

INPUT_TEXT = sys.stdin.read()

# Initialize parser with structure definition
parser = CStructParser(INPUT_TEXT, endian='little', debug=True)

fields: dict[str, dict[str, StructField]] = parser.struct_fields

# --- std430 base alignment/size table (bytes) ---
# type_name -> (size, alignment)
KNOWN_TYPES = {
    "float": (4, 4), "int": (4, 4), "uint": (4, 4), "unsigned int": (4, 4), "bool": (4, 4),
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
    "unsigned int": "np.uint32",
    "bool": "np.int32",
    "double": "np.float64",
}


def align_up(n, a):
    return ((n + a - 1) // a) * a

def get_dtype_name(struct_name: str):
    return f"dtype_{struct_name.replace(' ','_')}"
def get_c_name(struct_name: str):
    return f"s_{struct_name}"

py = "import numpy as np\n\n"
glsl = ""
c = "#include <stdbool.h>\ntypedef unsigned int uint;\n"

for struct_name in fields:
    struct = fields[struct_name]

    print(f"==================== working on {struct_name}")

    # vec2/vec3/vec4 etc are GLSL builtins -- skip emitting a glsl struct,
    # and don't recompute their alignment (it's hardcoded above, since it
    # can't be derived from their member floats: e.g. vec3's 3 floats sum
    # to align 4, but GLSL still aligns vec3 itself to 16).
    glsl_skip = struct_name in KNOWN_TYPES

    if not glsl_skip:
        glsl += f"struct {struct_name} {{\n"
    py += f"{get_dtype_name(struct_name)} = np.dtype([\n"
    c += f"typedef struct {get_c_name(struct_name)} {{\n"

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
                c += f"\tchar _pad{pad_idx}[{gap}];\n"
                pad_idx += 1
                offset = aligned_offset
            max_align = max(max_align, field_align)

        glsl_array = f"[{val.array_size}]" if val.array_size is not None else ""
        py_array = f", {val.array_size}" if val.array_size is not None else ""

        is_struct = not val.type_name in PY_TYPE_LUT.keys()

        py_type = get_dtype_name(val.type_name) if is_struct else PY_TYPE_LUT[val.type_name]
        c_type = get_c_name(val.type_name) if is_struct else val.type_name


        if not glsl_skip:
            glsl += f"\t{val.type_name} {val.name}{glsl_array};\n"
        py += f"\t('{val.name}', {py_type}{py_array}),\n"
        c += f"\t{c_type} {val.name}{glsl_array};\n"

        offset += field_size

    if not glsl_skip:
        # struct_align = align_up(max_align, 16)
        struct_align = max_align
        final_size = align_up(offset, struct_align)
        trailing_gap = final_size - offset
        if trailing_gap > 0:
            # print(f"on the end...")
            # print(f" {offset=}")
            # print(f" {final_size=}")
            # print(f" adding gap of {trailing_gap}")
            py += f"\t('_pad{pad_idx}', np.uint8, {trailing_gap}),\n"
            c += f"\tchar _pad{pad_idx}[{trailing_gap}];\n"
        KNOWN_TYPES[struct_name] = (final_size, struct_align)
        glsl += "};\n"

    py += "])\n"
    c += f"}} {get_c_name(struct_name)};\n"


# -------------------------------------------------------------------------------------------------
# process #define's

with open("struct_def.h",'r') as f:
    for line in f:
        # print(line)
        m = re.match(r"^#define\s+(?P<name>\w+)\s+(?P<value>.*)\s+$",line)
        if m:
            print(m.groupdict())
            py += f"{m.group('name')} = {m.group('value')}\n"
            # glsl and c have the same syntax
            glsl += line
            c += line


# -------------------------------------------------------------------------------------------------



with open("glsl/structs.glsl", 'w') as f:
    f.write(glsl)
with open("structs.py", 'w') as f:
    f.write(py)
with open("structs.h", 'w') as f:
    f.write(c)