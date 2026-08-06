all: structs.glsl structs.py

structs.glsl structs.py: structs.h
	gcc -E structs.h | python3 structgen.py

