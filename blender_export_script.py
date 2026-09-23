import bpy
import os

if not 'OUT_PATH' in os.environ:
    print("you need to provide the OUT_PATH environment variable")
    exit(1)

bpy.ops.wm.obj_export(
    filepath=os.environ['OUT_PATH'],
    export_uv=False,
    export_normals=True,
    export_pbr_extensions=True,
    export_triangulated_mesh=True
    )