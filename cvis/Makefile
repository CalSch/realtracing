cimgui/libcimgui.a:
	$(MAKE) -C cimgui static

# TODO: proper deps
rlImGui/rlImGui.o:
	cd rlImGui && g++ rlImGui.cpp -c -I../cimgui/imgui/

cvis: cvis.c ../structs.h cimgui/libcimgui.a rlImGui/rlImGui.o
	gcc -o $@ $< -lraylib -lm rlImGui/rlImGui.o cimgui/libcimgui.a -lstdc++ -O3 -ffast-math

../structs.h:
	$(MAKE) -C .. structs.h

all: cvis

clean:
	rm -vf cvis rlImGui/rlImGui.o
	$(MAKE) -C cimgui clean

.PHONY: cimgui/libcimgui.a clean ../structs.h