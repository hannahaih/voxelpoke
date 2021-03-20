from ursina import *
from collections import namedtuple
import json

# import pyximport; pyximport.install(language_level=3) # easy way to import .pyx files, auto-compiles
# from voxels_to_mesh import voxels_to_mesh
# from grid_to_cubes import grid_to_cubes
Size = namedtuple('Size', ['x','y','z'])

# window.vsync = False
chunk_size = Size(32, 32, 32)
cube = Entity(model='cube', enabled=False).model
cube.vertices = [Vec3(*e)+Vec3(.5,.5,.5) for e in cube.vertices]

cube_model = load_model('cube', application.internal_models_compressed_folder)
brush = Entity(model='wireframe_cube', color=color.green, always_on_top=True, origin=(-.5,-.5,-.5))
# brush.model.mode = 'line'
# brush.model.generate()

cube_verts = [
    (0,0,0), (1,0,0), (1,0,1), (0,0,1),
    (0,1,0), (1,1,0), (1,1,1), (0,1,1)
]

'''
   7-------6
  /|      /|
 / |     / |
4--|----5  |
|  3----|--2
| /     | /
0-------1
'''

cube_side_uvs = ((0,0), (1,0), (0,1), (0,1), (1,0), (1,1))
cube_sides = (
    [cube_verts[i] for i in (1,2,5, 5,2,6)], # right
    [cube_verts[i] for i in (3,0,7, 7,0,4)], # left
    [cube_verts[i] for i in (4,5,7, 7,5,6)], # up
    [cube_verts[i] for i in (3,2,0, 0,2,1)], # down
    [cube_verts[i] for i in (2,3,6, 6,3,7)], # forward
    [cube_verts[i] for i in (0,1,4, 4,1,5)]  # back
)

class Chunk(Entity):
    def __init__(self, size=chunk_size, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.grid = [[[0 for z in range(size.x)]for y in range(size.y)] for x in range(size.z)]
        self.model = Mesh(vertices=[], uvs=[])
        self.texture = 'white_cube'
        # self.colliders = []
        self.render()
        # self.edges = Entity(parent=self, model=copy(brush.model), color=color.red, scale=size)


        for key, value in kwargs.items():
            setattr(self, key ,value)

    def render(self):
        t = time.perf_counter()
        self.model.vertices, self.model.uvs = voxels_to_mesh(self.grid) # .035, .01
        print(time.perf_counter() - t)
        self.model.generate()


def voxels_to_mesh(voxels):
    vertices = []
    uvs = []
    width = len(voxels)
    height = len(voxels[0])
    depth = len(voxels[0][0])
    for x in range(width):
        for y in range(height):
            for z in range(depth):

                if voxels[x][y][z] == 0:
                    continue

                r, l, u, d, f, b = 0, 0, 0, 0, 0, 0     # right, left, up, down, forward, back

                # make sure we only get neightbors within bounds, otherwise stay as 0
                if x < width-1:
                    r = voxels[x+1][y][z]
                if x > 0:
                    l = voxels[x-1][y][z]
                if y < height-1:
                    u = voxels[x][y+1][z]
                if y > 0:
                    d = voxels[x][y-1][z]
                if z < depth-1:
                    f = voxels[x][y][z+1]
                if z > 0:
                    b = voxels[x][y][z-1]

                neighbors = (r, l, u, d, f, b)

                if neighbors == (1,1,1,1,1,1):
                    continue

                for i, e in enumerate(neighbors):
                    if not e:
                        vertices.extend([(e[0]+x, e[1]+y, e[2]+z) for e in cube_sides[i]])
                        uvs.extend(cube_side_uvs)

    return vertices, uvs


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='quad', origin_y=-.5)
        self.speed = 5
        self.vertical_speed = 10

        self.mouse_rotation_speed = 40
        self.controller_rotation_speed = 80
        self.zoom_speed = 10

        self.camera_pivot = Entity(parent=self, y=.5)

        camera.parent = self.camera_pivot
        camera.position = (0,0,-8)
        camera.rotation = (0,0,0)
        camera.fov = 90
        mouse.locked = True


        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        self.rotation_y += ((mouse.velocity.x * self.mouse_rotation_speed)
            - (held_keys['gamepad right stick x'] * time.dt * self.controller_rotation_speed))

        self.camera_pivot.rotation_x -= ((mouse.velocity.y * self.mouse_rotation_speed)
            + (held_keys['gamepad right stick y'] * time.dt * self.controller_rotation_speed)
            )

        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        self.direction += Vec3(
            self.forward *  held_keys['gamepad left stick y']
            + self.right *  held_keys['gamepad left stick x']
            )


        self.position += self.direction * self.speed * time.dt
        self.y += (held_keys['e']+held_keys['gamepad right trigger'] - held_keys['q']-held_keys['gamepad left trigger']) * self.vertical_speed * time.dt

        camera.z += held_keys['gamepad right stick y'] * time.dt * self.zoom_speed
        # camera.z = clamp(camera.z, -1, -30)


    def input(self, key):
        if key == 'scroll down':
            camera.z -= 1
        if key == 'scroll up':
            camera.z += 1

        if key == 'shift':
            self.speed *= 2
        if key == 'shift up':
            self.speed /= 2

        global brush_shape
        if key == '+' or key == Keys.gamepad_right_shoulder:
            brush.scale += Vec3(1,1,1)
            brush_shape = [[[1 for z in range(int(brush.scale.x))]for y in range(int(brush.scale.y))] for x in range(int(brush.scale.z))]
        if key == '-' or key == Keys.gamepad_left_shoulder:
            brush.scale -= Vec3(1,1,1)
            brush.scale = Vec3(max(brush.scale.x, 1), max(brush.scale.y, 1), max(brush.scale.z, 1))
            brush_shape = [[[1 for z in range(int(brush.scale.x))]for y in range(int(brush.scale.y))] for x in range(int(brush.scale.z))]

        # if held_keys['control'] and key == 'p':
        #     camera.orthographic = not camera.orthographic


app = Ursina()
import noise
from noise import *
from ursina.shaders import lit_with_shadows_shader
# chunk.shader = lit_with_shadows_shader

num_chunks = 1
chunks = [[Chunk(position=(x*chunk_size.x, 0, z*chunk_size.z), shader=lit_with_shadows_shader) for z in range(num_chunks)] for x in range(num_chunks)]
# chunks = []
for chunk_x in range(num_chunks):
    for chunk_z in range(num_chunks):
        chunk = chunks[chunk_x][chunk_z]

        # # loop through each chunk
        # for z in range(chunk_size.z):
        #     for x in range(chunk_size.x):
        #         noise = pnoise2(
        #             (x / chunk_size.x) + chunk_x,
        #             (z / chunk_size.z) + chunk_z,
        #             # x + (chunk_x*chunk_size) / chunk_size,
        #             # z + (chunk_z*chunk_size) / chunk_size,
        #             octaves=3, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)
        #         noise = int((noise+.5)*chunk_size.y)
        #         for y in range(noise):
        #             chunk.grid[x][y][z] = 1

        for x in range(chunk_size.x):
            for z in range(chunk_size.z):
                for y in range(1):
                    chunks[chunk_x][chunk_z].grid[x][y][z] = 1

        chunk.render()


brush.scale = 1
brush_shape = [[[1 for z in range(int(brush.scale.x))]for y in range(int(brush.scale.y))] for x in range(int(brush.scale.z))]



def update():
    brush.position = [floor(e) for e in player.position]
    #
    if mouse.left or held_keys['space'] or mouse.right or held_keys['gamepad a']:
        # for chunk in chunks:
        x, y, z = [int(e) for e in player.get_position(relative_to=chunk)]
        # print(x,y,z)
        org_grid = deepcopy(chunk.grid)


        if x >= 0 and x < chunk_size.x and y >= 0 and y < chunk_size.y and z >= 0 and z < chunk_size.z:
            if mouse.left or held_keys['space'] or held_keys['gamepad a']:
                # if not chunk.grid[x][y][z]:
                for brush_x in range(len(brush_shape)):
                    for brush_y in range(len(brush_shape[0])):
                        for brush_z in range(len(brush_shape[0][0])):
                            if brush_shape[brush_x][brush_y][brush_z]:
                                if x+brush_x < chunk_size.x and y+brush_y < chunk_size.y and z+brush_z < chunk_size.z:
                                    chunk.grid[x+brush_x][y+brush_y][z+brush_z] = 1

            elif mouse.right or held_keys['gamepad x']:
                for brush_x in range(len(brush_shape)):
                    for brush_y in range(len(brush_shape[0])):
                        for brush_z in range(len(brush_shape[0][0])):
                            if brush_shape[brush_x][brush_y][brush_z]:

                                chunk.grid[x+brush_x][y+brush_y][z+brush_z] = 0
            if not chunk.grid == org_grid:
                t = time.perf_counter()
                chunk.render()
                # print(time.perf_counter() - t, 1/60)



from ursina.prefabs.file_browser import FileBrowser
from ursina.prefabs.file_browser_save import FileBrowserSave
file_browser =      FileBrowser(start_path=Path('.'), file_types=('.json'), enabled=False, ignore_paused=True)
file_browser_save = FileBrowser(file_types=('.json'), enabled=False, ignore_paused=True)
current_file = None

def on_submit(value):
    for path in value:
        print('---', path)
        save()

file_browser_save.on_submit = on_submit
file_browser_save.on_enable = Sequence(Func(file_browser_save.on_enable), Func(setattr, mouse, 'locked', False))
# def test():
#     application.paused = True
#     mouse.locked = True

# file_browser_save.on_enable = test

def save_current_file():
    if not current_file:
        print('error: trying to save() when current_file is None, use save_as() instead')
        return

    with open(current_file, 'w') as file:
        json.dump(chunk.grid, file)


def save_as(path):
    with open(path, 'w') as file:
        json.dump(chunk.grid, file)


def load():
    with open('test.json', 'r') as file:
        chunk.grid = json.load(file)
        chunk.render()


def input(key):
    if held_keys['control'] and key == 's':
        if current_file:
            save_current_file()
        elif not file_browser_save.enabled:
            file_browser_save.enabled = True

    if held_keys['control'] and key == 'l':
        load()



# 125 641 blocks
from ursina.shaders import unlit_shader
player = Player(position=Vec3(num_chunks/2*chunk_size.x,0,num_chunks/2*chunk_size.z), model=None)
# player.graphics = Entity(parent=player, model='quad', origin_y=-.5, shader=unlit_shader, texture='opossum', scale=(1,2))
# brush.model = None

sky = Sky(color=color.hex('#b8523b'))
Entity(parent=render, model='plane', scale=9999, color='#b8523b')
# ground = Entity(model='plane', origin=(-.5,0,-.5), scale=16, texture='grass', texture_scale=(16,16))

DirectionalLight(rotation_x=30)

scene.fog_color = sky.color
app.run()
