all: structs.glsl structs.py

structs.glsl structs.py: structs.h glsl_include.h structgen.py
	gcc -E structs.h | python3 structgen.py

gridview: gridview.c
	gcc gridview.c -O2 -o gridview -lraylib -lGL -lm -lpthread -ldl -lrt -lX11
