from CStructParser.CStructParser import CStructParser, StructField
import pprint
import sys

# Initialize parser with structure definition
parser = CStructParser(sys.stdin.read(), endian='little', debug=True)

# pprint.pprint(parser.struct_fields)

fields: dict[str,dict[str,StructField]] = parser.struct_fields


py="""\
import numpy as np
"""
glsl=""


for struct_name in fields:
    struct = fields[struct_name]

    # in glsl, skip vector types (they're built in). but dont skip in python
    glsl_skip = False
    if struct_name in ['vec2','vec3','vec4']:
        glsl_skip = True

    if not glsl_skip: glsl += f"struct {struct_name} {{\n"
    py += f"dtype_{struct_name} = np.dtype([\n"

    for field in struct:
        val = struct[field]
        # print(val.name, val.type_name, val.array_size)

        glsl_array = f"[{val.array_size}]" if val.array_size is not None else ""

        py_type = val.type_name
        PY_TYPE_LUT = {
            "float": "np.float32",
            "int": "np.int32",
        }
        if py_type in PY_TYPE_LUT.keys():
            py_type = PY_TYPE_LUT[py_type]
        else:
            py_type = f"dtype_{py_type}"

        py_array = f", {val.array_size}" if val.array_size is not None else ""

        if not glsl_skip: glsl += f"\t{val.type_name} {val.name}{glsl_array};\n"
        py += f"\t('{val.name}', {py_type}{py_array}),\n"

    py += "])\n"
    if not glsl_skip: glsl += "};\n"

with open("structs.glsl", 'w') as f:
    f.write(glsl)
with open("structs.py", 'w') as f:
    f.write(py)

