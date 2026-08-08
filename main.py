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




GROUP_SIZE_X = 1024

RESOLUTION = [4096*8,4096*8]
# RESOLUTION = [128*8, 96*8]

COMPUTE_SHADER = open("theshader.glsl",'r').read()
COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", lambda m: open(m.group(1),'r').read(), COMPUTE_SHADER)
COMPUTE_SHADER += f"\nlayout(local_size_x = {GROUP_SIZE_X}) in;\n"

with open(".output.glsl",'w') as f:
    f.write(COMPUTE_SHADER)

ctx = moderngl.create_standalone_context(require=430)

compute = ctx.compute_shader(COMPUTE_SHADER)

def ceiling_divide(x: int, y: int) -> int:
    return (x + y - 1) // y



print(" making input buf")
INPUT_BUF_INIT = dict_to_struct({
    "resolution": RESOLUTION,
    "win_min": [-2, -1],
    "win_max": [0.5, 1],
}, structs.dtype_Input)
input_buf = ctx.buffer(INPUT_BUF_INIT.tobytes())
input_buf.bind_to_storage_buffer(1)

result_buf: moderngl.Buffer = ctx.buffer(b"67")


def remake_result_buf(size):
    global result_buf
    print(" making result buf")
    RESULT_BUF_INIT = np.zeros(size, dtype=structs.dtype_Result)
    print(f"  {RESULT_BUF_INIT.nbytes=}")
    result_buf.release()
    result_buf = ctx.buffer(RESULT_BUF_INIT.tobytes())
    result_buf.bind_to_storage_buffer(0)



def run_batch(start_idx: int, batch_size: int) -> np.ndarray:

    if result_buf.size != batch_size*structs.dtype_Result.itemsize:
        print(f" i need to remake the result buffer!")
        print(f"  {result_buf.size=}")
        print(f"  {batch_size*structs.dtype_Result.itemsize=}")
        remake_result_buf(batch_size)

    compute["start_idx"] = start_idx

    group_count_x = ceiling_divide(batch_size, GROUP_SIZE_X)
    print(f" {group_count_x=}")

    print(" ok tim to go!")
    compute.run(group_x=group_count_x)

    print(" done! readback")
    # read back and reinterpret as the same struct array
    result = np.frombuffer(result_buf.read(), dtype=structs.dtype_Result)

    return result


def main():

    print(f"{os.getpid() = }")

    # N = 100
    N = RESOLUTION[0] * RESOLUTION[1]
    # CHUNKS = 8
    # CHUNK_SIZE=N//CHUNKS
    CHUNK_SIZE = 2**16
    CHUNKS = ceiling_divide(N, CHUNK_SIZE)

    print(f"{CHUNKS=}")
    print(f"{CHUNK_SIZE=}")

    time.sleep(3)

    start = time.perf_counter()
    chunk_results = []
    for i in range(CHUNKS):
        print(f"chunk {i}")
        new_data = run_batch(i*CHUNK_SIZE, CHUNK_SIZE)
        # new_data.dump(f"chunk{i:04}.bin")
        print(f"chunk {i} done")
        chunk_results.append(new_data)
    results = np.concatenate(chunk_results)
    del chunk_results

    end = time.perf_counter()
    print(f"{end-start=}")
    # result = run_batch(1,N)

    # print(result[:5])
    def struct_to_dict(x):
        if x.dtype.names is None:
            return x.tolist() if x.shape else x.item()
        return {name: struct_to_dict(x[name]) for name in x.dtype.names if not name.startswith("_")}


    if False:
        print(results[0])
        print(results[1])
        pprint(struct_to_dict(results[0]))
        pprint(struct_to_dict(results[1]))
        pprint(struct_to_dict(results[2]))
        print("------")
        pprint(struct_to_dict(results[N-3]))
        pprint(struct_to_dict(results[N-2]))
        pprint(struct_to_dict(results[N-1]))
    print("dtype itemsize:", structs.dtype_Result.itemsize)

    if False:
        for y in range(RESOLUTION[1]):
            for x in range(RESOLUTION[0]):
                v = struct_to_dict(results[x+y*RESOLUTION[0]])["time_to_escape"]
                print(f"\x1b[48;5;{v+16}m  ", end="")
            print()

    print(f"{len(results)=}")
    print(f"{results[0].nbytes=}")
    print(f"{results.nbytes=}")
    print('saving...')
    with open('results.bin','wb') as f:
        f.write(bytes(results))
    # print("jason!")
    # with open('results.json', 'w') as f:
    #     json.dump([struct_to_dict(r) for r in results], f)

main()