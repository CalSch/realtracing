import sys
import re
import structs
import numpy as np

inp = np.zeros(1, dtype=structs.dtype_Input)[0]


path = sys.argv[1]

vertices = []
normals = []
tris = []

def add_tri(t):
	print(f"{len(inp['scene']['tris'])=}")
	idx = inp['scene']['tri_count']
	for p in [(0,'p0'),(1,'p1'),(2,'p2')]:
		inp['scene']['tris'][idx][p[1]]['x'] = t[p[0]][0]
		inp['scene']['tris'][idx][p[1]]['y'] = t[p[0]][1]
		inp['scene']['tris'][idx][p[1]]['z'] = t[p[0]][2]
	inp['scene']['tri_count'] += 1


with open(path, "r") as f:
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
			print(line)
			m = re.match(r"f (?P<v1>\d+)//(?P<vn1>\d+) (?P<v2>\d+)//(?P<vn2>\d+) (?P<v3>\d+)//(?P<vn3>\d+)", line)
			(v1, vn1, v2, vn2, v3, vn3) = list(int(s)-1 for s in m.groupdict().values())
			# print(v1, vn1, v2, vn2, v3, vn3)
			tris.append((v1, v2, v3, vn1, vn2, vn3))

# print(tris)
# with open("out.py", "w") as f:
	# f.write("from thingy import add_tri, save_scene\n")
	for tri in tris:
		t = ""
		for v in tri[:3]:
			# print(v, len(vertices))
			t += f" {vertices[v]}, "
		fn = [0,0,0]
		for n in tri[3:]:
			for i in range(3):
				fn[i] += normals[n][i]
		# TODO: normalize the normal
		# for i in range(3):
		# 	fn[i] /= 3
			
		t = t[:-2]

		add_tri([vertices[tri[n]] for n in range(3)])

		# f.write(f"add_tri([{t}])\n")
	# f.write("save_scene('out.scene')\n")
	# print(t + str(fn))

with open("out.scene", "wb") as f:
	f.write(inp.tobytes())


# print(vertices)
