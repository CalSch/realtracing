structs.glsl: structs.h
	gcc -E structs.h | python3 structgen.py
