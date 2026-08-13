all: glsl/structs.glsl structs.py structs.h

glsl/structs.glsl structs.py structs.h: struct_def.h glsl_include.h structgen.py
	gcc -E struct_def.h | python3 structgen.py

cvis: cvis.c structs.h
	gcc -o $@ $< -lraylib -O0
