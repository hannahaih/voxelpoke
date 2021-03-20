from ursina import *

app = Ursina()


terrain = Entity(model='blocky_terrain', color=color.light_gray, scale=.25)

from time import perf_counter
t = perf_counter()
# tileset = load_blender_scene('tileset', models_only=True, reload=False)
# print('-----------', tileset)
# print(perf_counter() - t)
# Entity(model=tileset['roof'], origin=(-.5,-.5,-.5))

# ground = Entity(model='plane', collider='box', scale=8, texture='white_cube', texture_scale=(8,8), origin=(-.5,0,-.5))
# cursor = Entity(model=Cube(mode='line'), origin=(-.5,-.5,-.5), color=color.red, always_on_top=True)
# grid = [[[None for z in range(8)] for y in range(8)] for x in range(8)]


# def update():
#     if mouse.hovered_entity == ground:
#         cursor.x = mouse.point.x * 8
#         cursor.z = mouse.point.z * 8
#         cursor.position = round(cursor.position, 0)


# def input(key):
#     if key == 'left mouse down':
#         x, y, z = int(cursor.x), int(cursor.y), int(cursor.z)
#         if not grid[x][y][z]:
#             grid[x][y][z] = Entity(model='cube', color=color.azure, texture='white_cube', origin=(-.5,-.5,-.5), position=Vec3(x,y,z))
#         else:
#             destroy(grid[x][y][z])
#
#
#     if key == 'd': cursor.x += 1
#     if key == 'a': cursor.x -= 1
#
#     if key == 'e': cursor.y += 1
#     if key == 'q': cursor.y -= 1
#
#     if key == 'w': cursor.z += 1
#     if key == 's': cursor.z -= 1
#
#     cursor.x = clamp(cursor.x, 0, 7)
#     cursor.y = clamp(cursor.y, 0, 7)
#     cursor.z = clamp(cursor.z, 0, 7)

EditorCamera(rotation_x=90)
from ursina.lights import DirectionalLight
from ursina.shaders import lit_with_shadows_shader
# ground.shader = lit_with_shadows_shader
# shader = Shader.load(Shader.SL_GLSL, "lighting.vert", "lighting.frag")
terrain.shader = lit_with_shadows_shader
sun = DirectionalLight(rotation_z=30, model='cube', origin_z=-.5)
# sun.get_lens().set_near_far(1, 30)
# sun.get_lens().set_film_size(20, 40)
# sun.show_frustum()
sun._light.set_shadow_caster(True, 1024, 1024)

bmin, bmax = scene.get_tight_bounds(sun)
lens = sun._light.get_lens()
lens.set_film_offset((bmin.xy + bmax.xy) * 0.5)
lens.set_film_size(bmax.xy - bmin.xy)
lens.set_near_far(bmin.z, bmax.z)

def update():
    sun.rotation_x += held_keys['d'] * 1
    sun.rotation_x -= held_keys['a'] * 1

# ground.set_shader(shader)


app.run()
