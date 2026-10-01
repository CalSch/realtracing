import sys
import re
import structs
import numpy as np
import random

INP_BUF = np.zeros(1, dtype=structs.dtype_Input)[0]

path = sys.argv[1]

materials = []
vertices = []
normals = []
tris = []

INP_BUF['scene']['materials'][1]['c_diffuse']['x'] = 0.9
INP_BUF['scene']['materials'][1]['c_diffuse']['y'] = 0.9
INP_BUF['scene']['materials'][1]['c_diffuse']['z'] = 0.1

INP_BUF['scene']['materials'][2]['c_diffuse']['x'] = 0.1
INP_BUF['scene']['materials'][2]['c_diffuse']['y'] = 0.9
INP_BUF['scene']['materials'][2]['c_diffuse']['z'] = 0.9

INP_BUF['scene']['materials'][3]['c_diffuse']['x'] = 0.9
INP_BUF['scene']['materials'][3]['c_diffuse']['y'] = 0.1
INP_BUF['scene']['materials'][3]['c_diffuse']['z'] = 0.9

def add_tri(t, mat):
	if mat not in materials:
		materials.append(mat)
	mat_idx = materials.index(mat)
	# print(f"{len(INP_BUF['scene']['tris'])=}")
	idx = INP_BUF['scene']['tri_count']
	for p in [(0,'p0'),(1,'p1'),(2,'p2')]:
		INP_BUF['triangles'][idx][p[1]]['x'] = t[p[0]][0]
		INP_BUF['triangles'][idx][p[1]]['y'] = t[p[0]][1]
		INP_BUF['triangles'][idx][p[1]]['z'] = t[p[0]][2]
	INP_BUF['triangles'][idx]['material_idx'] = mat_idx
	INP_BUF['scene']['tri_count'] += 1


with open(path, "r") as f:
	current_mat = None
	for line in f.readlines():
		line = line[:-1]
		if line.startswith("v "):
			# print(line)
			m = re.match(r"v (?P<x>-?\d+\.\d+) (?P<y>-?\d+\.\d+) (?P<z>-?\d+\.\d+)", line)
			x, y, z = float(m.groupdict()["x"]), float(m.groupdict()["y"]), float(m.groupdict()["z"])
			vertices.append((x, y, z))
		elif line.startswith("vn "):
			m = re.match(r"vn (?P<x>-?\d+\.\d+) (?P<y>-?\d+\.\d+) (?P<z>-?\d+\.\d+)", line)
			x, y, z = float(m.groupdict()["x"]), float(m.groupdict()["y"]), float(m.groupdict()["z"])
			normals.append((x, y, z))
		elif line.startswith("f "):
			# print(line)
			m = re.match(r"f (?P<v1>\d+)//(?P<vn1>\d+) (?P<v2>\d+)//(?P<vn2>\d+) (?P<v3>\d+)//(?P<vn3>\d+)", line)
			(v1, vn1, v2, vn2, v3, vn3) = list(int(s)-1 for s in m.groupdict().values())
			# print(v1, vn1, v2, vn2, v3, vn3)
			tris.append((v1, v2, v3, vn1, vn2, vn3, current_mat))
		elif line.startswith("usemtl "):
			# material = line[len("usemtl "):].strip()
			m = re.match(r"usemtl\s+(.*)", line)
			mat = m.group(1)
			current_mat = mat
			print(mat)

	print(f"{len(vertices)=}")
	print(f"{len(tris)=}")
# print(tris)
# with open("out.py", "w") as f:
	# f.write("from thingy import add_tri, save_scene\n")
	for tri in tris:
		t = ""
		for v in tri[:3]:
			# print(v, len(vertices))
			t += f" {vertices[v]}, "
		fn = [0,0,0]
		for n in tri[3:6]:
			for i in range(3):
				fn[i] += normals[n][i]
		# TODO: normalize the normal
		# for i in range(3):
		# 	fn[i] /= 3
			
		t = t[:-2]

		add_tri([vertices[tri[n]] for n in range(3)], tri[6])

		# f.write(f"add_tri([{t}])\n")
	# f.write("save_scene('out.scene')\n")
	# print(t + str(fn))

with open("inputs.bin", "wb") as f:
	f.write(INP_BUF.tobytes())

print("generated input data!")
print(f"{len(INP_BUF)=}")

# print(vertices)
