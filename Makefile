all: glsl/structs.glsl structs.py structs.h

glsl/structs.glsl structs.py structs.h: struct_def.h glsl_include.h structgen.py
	gcc -E struct_def.h | python3 structgen.py

cvis/cvis: cvis/cvis.c structs.h
	gcc -o $@ $< -lraylib -O3 -ffast-math

scene.obj scene.mtl: scene.blend
	OUT_PATH=scene.obj blender scene.blend --background --enable-autoexec --python-exit-code 1 --offline-mode --python blender_export_script.py

inputs.bin: structs.py scenegen.py scene.obj
	uv run scenegen.py scene.obj

results.bin: inputs.bin structs.py main.py glsl/*.glsl
	uv run main.py

clean:
	rm -vf .output.glsl cvis/cvis {inputs,results}.bin scene.{obj,mtl} structs.{h,py} glsl/structs.glsl
