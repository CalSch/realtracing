# import raylib as rl
import pyray as rl
import json
import math
import numpy as np
import structs

with open("results.bin", 'rb') as f:
    # data = json.load(f)
    data = np.frombuffer(f.read(), dtype=structs.dtype_Result)

SW=1270
SH=int(SW*3/4)



def data2vec3(data) -> rl.Vector3:
    return rl.Vector3(data['x'],data['y'],data['z'])





rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIGHDPI)
rl.init_window(SW,SH,"goo")

cam = rl.Camera3D(rl.Vector3(8,8,8),rl.Vector3(0,0,0),rl.Vector3(0,1,0),30)

rl.set_target_fps(60)

while not rl.window_should_close():

    rl.update_camera(cam,rl.CameraMode.CAMERA_ORBITAL)

    rl.begin_drawing()
    rl.begin_mode_3d(cam)

    rl.clear_background(rl.BLUE)

    rl.draw_grid(10,1)

    for res in data:
        orig = data2vec3(res["ray"]["origin"])
        dir = data2vec3(res["ray"]["dir"])

        rl.draw_sphere(orig, 0.05, rl.RED)
        rl.draw_line_3d(orig,rl.vector3_add(orig,rl.vector3_scale(dir,100)),rl.WHITE)
        
    rl.end_mode_3d()

    rl.draw_fps(10,10)

    rl.end_drawing()

rl.close_window()