from ursina import *

builtin_sum = sum
def sum(l):
    if isinstance(l[0], (tuple, Vec3)):
        import numpy as np
        l = [np.array(e) for e in l]
        return np.sum(l, axis=0)
    else:
        return builtin_sum(l)



app = Ursina()

grid = Entity(model='irregular_grid')
grid_mesh = grid.model
grid_mesh.vertices = [Vec3(*e) for e in grid_mesh.vertices]
buildings = Entity(model=Mesh(vertices=list(), triangles=list()))
building_mesh = buildings.model
ground_collider = Entity(model='plane', y=-.01, color=color.black, scale=50, collider='box')

quad_centers = list()

for quad in grid_mesh.triangles:
    center = [grid_mesh.vertices[e] for e in quad]
    center = sum(center)
    center = Vec3(*center) / 4
    quad_centers.append(center)
    # Entity(model='sphere', scale=.5, color=color.red, position=center, scale_y=.01)

def distance_from_mouse(e):
    return distance(e, mouse.world_point)

cursor = Entity(model='plane', color=color.orange, scale=.5)
def update():
    if not mouse.world_point:
        return
    # closest_point = min([distance(mouse.world_point, e) for e in quad_centers])
    closest_point = sorted(quad_centers, key=distance_from_mouse)[0]
    cursor.position = closest_point
    # print(quad_centers.index(closest_point))

def input(key):
    if key == 'left mouse down':
        closest_point = sorted(quad_centers, key=distance_from_mouse)[0]
        cursor.position = closest_point
        extrude(quad_centers.index(closest_point), 1, True)
        print('extrude:', quad_centers.index(closest_point))
        building_mesh.colorize()


def extrude(quad_index, amount=1, regenerate=True):
    quad = grid_mesh.triangles[quad_index]
    extra_tris = list()

    side_tris_bot = [len(building_mesh.vertices)+i for i in range(4)]
    side_tris_bot.append(side_tris_bot[0])
    side_tris_top = [len(building_mesh.vertices)+i+4 for i in range(4)]
    side_tris_top.append(side_tris_top[0])

    for i in range(4):
        extra_tris.append([side_tris_bot[i], side_tris_bot[i+1], side_tris_top[i+1], side_tris_top[i]])

    extra_tris.append(([len(building_mesh.vertices)+i+4 for i in range(4)])) # top


    building_mesh.vertices.extend([grid_mesh.vertices[i] for i in quad])
    building_mesh.vertices.extend([grid_mesh.vertices[i] + Vec3(0,amount,0) for i in quad])


    # added_cols = (color.color(0,0,extrusion_amount/5), ) * 4
    # print(added_cols)
    # grid_mesh.colors.extend(added_cols)
    # print('lol', extra_tris)
    building_mesh.triangles.extend(extra_tris)

    if regenerate:
        # building_mesh.generate()
        building_mesh.colorize()

extrude(80, random.uniform(0,5), True)

EditorCamera()
mouse.visible = False
app.run()
