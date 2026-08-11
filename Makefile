all: glsl/structs.glsl structs.py

glsl/structs.glsl structs.py: structs.h glsl_include.h structgen.py
	gcc -E structs.h | python3 structgen.py

