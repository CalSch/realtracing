# import raylib as rl
import pyray as rl
import json
import math

with open("results.json", 'r') as f:
    data = json.load(f)

SW=1270
SH=int(SW*3/4)
DW=128*8
DH=96*8

rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIGHDPI)
rl.init_window(SW,SH,"goo")

def win2data(x,y):
    return (int(x/SW*DW),int(y/SH*DH))
def data2win(x,y):
    return (int(x/DW*SW),int(y/DH*SH))
def complex2win(x,y):
    return (
        int(rl.remap(x, -2, 0.5, 0, SW)),
        int(rl.remap(y, -1, 1, 0, SH)),
    )

def create_img():
    img = rl.gen_image_color(SW,SH,rl.MAGENTA)
    for y in range(DH):
        for x in range(DW):
            i = x + y*DW
            v = data[i]['time_to_escape']
            sx, sy = data2win(x,y)
            w, h = data2win(2,2)
            c = rl.color_from_hsv(rl.remap(v, 0, 80, 0, 360), 1, 1)
            if v == 80:
                c = rl.BLACK
            rl.image_draw_rectangle(img,sx,sy,w,h,c)
    return img


IMG = create_img()
BACKGROUND = rl.load_texture_from_image(IMG)

while not rl.window_should_close():
    mx, my = win2data(rl.get_mouse_x()*1.6,rl.get_mouse_y()*1.6)

    i = mx+my*DW

    rl.begin_drawing()

    rl.clear_background(rl.BLUE)

    rl.draw_texture(BACKGROUND,0,0,rl.WHITE)

    if i>0 and i<=len(data):
        oldx, oldy = 0, 0
        for j in range(len(data[i]["iters"]["x"])):
            first = j==0
            # print(j)
            x = data[i]['iters']['x'][j]
            y = data[i]['iters']['y'][j]
            # print(x,y)
            sx, sy = complex2win(x, y)

            rl.draw_circle(sx,sy,4 if first else 2, rl.BLUE if first else rl.RED)
            if not first:
                rl.draw_line(oldx,oldy,sx,sy,rl.WHITE)

            oldx, oldy = sx, sy
        print(mx,my)

    rl.end_drawing()

rl.close_window()