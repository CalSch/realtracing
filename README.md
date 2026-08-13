real


things:
- `main.py`: compiles and runs the compute shader and saves the result to `results.bin`
    - you can control how many "samples" there are by changing `N`
- `structgen.py`: reads & parses `struct_def.h` to generate equal versions of `structs.{glsl,py,h}`
    - this is so we can have the same structs in GLSL, Python, and C
    - accounts for padding & layout stuff
    - depends on `CStructParser` from https://github.com/zavdimka/CStructParser
- `visualizer.py`: an old python visualizer that i stopped using bc its slow




ok so here's how you can see whats happening:

- generate `results.bin` with the compute shader: `make structs.py && uv run main.py`
- view the results in 3d: `make cvis && ./cvis`