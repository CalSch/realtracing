import moderngl
import numpy as np
import re
from pprint import pprint, pp
import structs
from typing import Any
import time
import json
import sys
import os
import random


# clud's code

def dict_to_struct(d: dict[str, Any] | list | tuple, dtype: np.dtype) -> np.void:
    arr = np.zeros(1, dtype=dtype)[0]
    for name in dtype.names:
        if isinstance(d, dict):
            if name not in d:
                continue  # leave field at its zero default
            val = d[name]
        else:
            val = d[dtype.names.index(name)]

        field_dtype = dtype[name]
        if field_dtype.names is not None:
            if field_dtype.shape:  # array of structs
                for i, item in enumerate(val):
                    arr[name][i] = dict_to_struct(item, field_dtype.base)
            else:
                # nested struct: accept a dict, or a list/tuple in field order
                arr[name] = dict_to_struct(val, field_dtype)
        else:
            arr[name] = val
    return arr

def struct_to_dict(x):
    if x.dtype.names is None:
        return x.tolist() if x.shape else x.item()
    return {name: struct_to_dict(x[name]) for name in x.dtype.names if not name.startswith("_")}



GROUP_SIZE_X = 256


COMPUTE_SHADER = open("glsl/theshader.glsl",'r').read()
COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", lambda m: open("glsl/"+m.group(1),'r').read(), COMPUTE_SHADER) # process #include's
COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", "", COMPUTE_SHADER) # remove all nested #include's
COMPUTE_SHADER += f"\nlayout(local_size_x = {GROUP_SIZE_X}) in;\n"

with open(".output.glsl",'w') as f:
    f.write(COMPUTE_SHADER)

ctx = moderngl.create_standalone_context(require=430)

print("compute shader compiling...")
compile_start = time.perf_counter()
compute = ctx.compute_shader(COMPUTE_SHADER)
compile_end = time.perf_counter()
print("compute shader done compiling")
print(f"took {compile_end-compile_start} sec")


def ceiling_divide(x: int, y: int) -> int:
    return (x + y - 1) // y


result_buf: moderngl.Buffer = ctx.buffer(b"67")

INPUT_BUF_INIT: np.void

def make_input_buf():
    global INPUT_BUF_INIT
    print("making input buf")

    with open("inputs.bin", "rb") as f:
        contents = f.read()
        print(f"{len(contents)=}")
        print(f"{structs.dtype_Input.itemsize=}")
        print(f"{structs.dtype_Scene.itemsize=}")
        INPUT_BUF_INIT = np.frombuffer(contents, structs.dtype_Input)

    # pprint(struct_to_dict(INPUT_BUF_INIT))
    
    input_buf = ctx.buffer(INPUT_BUF_INIT.tobytes())
    input_buf.bind_to_storage_buffer(1)



def remake_result_buf(size):
    global result_buf
    print("  making result buf")
    RESULT_BUF_INIT = np.zeros(size, dtype=structs.dtype_Result)
    print(f"    {RESULT_BUF_INIT.nbytes=}")
    result_buf.release()
    result_buf = ctx.buffer(RESULT_BUF_INIT.tobytes())
    result_buf.bind_to_storage_buffer(0)



def run_batch(start_idx: int, batch_size: int) -> np.ndarray:

    if result_buf.size != batch_size*structs.dtype_Result.itemsize:
        print(f"  i need to remake the result buffer!")
        print(f"    {result_buf.size=}")
        print(f"    {batch_size*structs.dtype_Result.itemsize=}")
        remake_result_buf(batch_size)

    try:
        compute["start_idx"] = start_idx
        compute["seed"] = random.randrange(0,1024) # TODO: better range
    except:
        print("WARNING: couldn't set one of the uniforms")
        print(list(compute))

    group_count_x = ceiling_divide(batch_size, GROUP_SIZE_X)
    print(f"  {group_count_x=}")

    print("  ok tim to go!")
    compute.run(group_x=group_count_x)

    print("  done! readback")
    # read back and reinterpret as the same struct array
    result = np.frombuffer(result_buf.read(), dtype=structs.dtype_Result)

    return result


def main():

    print(f"{os.getpid() = }")

    make_input_buf()

    with open("inputs.bin",'wb') as f:
        f.write(INPUT_BUF_INIT.tobytes())

    # N = 100
    N = 80000
    CHUNKS = 1
    CHUNK_SIZE=N//CHUNKS
    # CHUNK_SIZE = 2**24
    # CHUNKS = ceiling_divide(N, CHUNK_SIZE)

    print(f"{CHUNKS=}")
    print(f"{CHUNK_SIZE=}")

    # time.sleep(3)

    start = time.perf_counter()

    out_file = open('results.bin','wb')
    
    for i in range(CHUNKS):
        print(f"chunk {i}/{CHUNKS} = {i/CHUNKS*100:.4}%")
        new_data = run_batch(i*CHUNK_SIZE, CHUNK_SIZE)
        print(f"chunk {i} done")
        out_file.write(new_data.tobytes())


    out_file.close()

    end = time.perf_counter()
    print(f"{end-start=}")


    # result = run_batch(1,N)

    # print(result[:5])


main()