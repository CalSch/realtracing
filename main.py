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

def struct_to_dict(x):
	if x.dtype.names is None:
		return x.tolist() if x.shape else x.item()
	return {name: struct_to_dict(x[name]) for name in x.dtype.names if not name.startswith("_")}



GROUP_SIZE_X = 1024


COMPUTE_SHADER = open("glsl/theshader.glsl",'r').read()
COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", lambda m: open("glsl/"+m.group(1),'r').read(), COMPUTE_SHADER) # process #include's
COMPUTE_SHADER = re.sub(r"#include \"(.*)\"", "", COMPUTE_SHADER) # remove all nested #include's
COMPUTE_SHADER += f"\nlayout(local_size_x = {GROUP_SIZE_X}) in;\n"

with open(".output.glsl",'w') as f:
	f.write(COMPUTE_SHADER)

ctx = moderngl.create_standalone_context(require=430)

compute = ctx.compute_shader(COMPUTE_SHADER)

def ceiling_divide(x: int, y: int) -> int:
	return (x + y - 1) // y


result_buf: moderngl.Buffer = ctx.buffer(b"67")

def make_input_buf():
	print("making input buf")
	with open("../out.scene", "rb") as f:
		INPUT_BUF_INIT = np.frombuffer(f.read(), structs.dtype_Input)
	# INPUT_BUF_INIT = dict_to_struct({
	#     # "scene": {
	#     #     "tris": [
	#     #         {"p0": [0,0,2], "p1": [0,1,2], "p2": [1,0,2]}
	#     #     ],
	#     #     "tri_count": 1
	#     # }
	# }, structs.dtype_Input)
	# # INPUT_BUF_INIT = np.array([], dtype=structs.dtype_Input)

	# def add_tri(t: list[list[float]]):
	#     idx = INPUT_BUF_INIT['scene']['tri_count']
	#     for p in [(0,'p0'),(1,'p1'),(2,'p2')]:
	#         INPUT_BUF_INIT['scene']['tris'][idx][p[1]]['x'] = t[p[0]][0]
	#         INPUT_BUF_INIT['scene']['tris'][idx][p[1]]['y'] = t[p[0]][1]
	#         INPUT_BUF_INIT['scene']['tris'][idx][p[1]]['z'] = t[p[0]][2]
	#     INPUT_BUF_INIT['scene']['tri_count'] += 1

	# add_tri([[-3,0,2],[2,4,2],[2,-2,2]])
	# add_tri([[0,0,1],[0,1,1],[1,0,1.5]])

	pprint(struct_to_dict(INPUT_BUF_INIT))
	
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
	except:
		print("WARNING: couldn't set the start_idx")

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

	# N = 100
	N = 8000
	CHUNKS = 1
	CHUNK_SIZE=N//CHUNKS
	# CHUNK_SIZE = 2**24
	# CHUNKS = ceiling_divide(N, CHUNK_SIZE)

	print(f"{CHUNKS=}")
	print(f"{CHUNK_SIZE=}")

	# time.sleep(3)

	start = time.perf_counter()
	chunk_results = []

	out_file = open('results.bin','wb')
	
	for i in range(CHUNKS):
		print(f"chunk {i}/{CHUNKS} = {i/CHUNKS*100:.4}%")
		new_data = run_batch(i*CHUNK_SIZE, CHUNK_SIZE)
		# new_data.dump(f"chunk{i:04}.bin")
		print(f"chunk {i} done")
		out_file.write(new_data.tobytes())
		chunk_results.append(new_data)

	if len(chunk_results) > 0:
		print("concatenating...")
		results = np.concatenate(chunk_results)
	else:
		results = []

	del chunk_results

	end = time.perf_counter()
	print(f"{end-start=}")
	# result = run_batch(1,N)

	# print(result[:5])


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


main()