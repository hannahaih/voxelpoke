from ursina import *
from collections import namedtuple
import json

Size = namedtuple('Size', ['x','y','z'])

chunk_size = Size(32, 32, 32)
cube = Entity(model='cube', enabled=False).model
cube.vertices = [Vec3(*e)+Vec3(.5,.5,.5) for e in cube.vertices]

cube_model = load_model('cube', application.internal_models_compressed_folder)
brush = Entity(model='wireframe_cube', color=color.green, always_on_top=True, origin=(-.5,-.5,-.5))

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

cube_side_uvs = tuple(e/8 for e in (Vec2(0,0), Vec2(1,0), Vec2(0,1), Vec2(0,1), Vec2(1,0), Vec2(1,1)))
cube_sides = (
    [cube_verts[i] for i in (1,2,5, 5,2,6)], # right
    [cube_verts[i] for i in (3,0,7, 7,0,4)], # left
    [cube_verts[i] for i in (4,5,7, 7,5,6)], # up
    [cube_verts[i] for i in (3,2,0, 0,2,1)], # down
    [cube_verts[i] for i in (2,3,6, 6,3,7)], # forward
    [cube_verts[i] for i in (0,1,4, 4,1,5)]  # back
)
tileset_index = 1

class Chunk(Entity):
    def __init__(self, size=chunk_size, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.grid = [[[0 for z in range(size.x)]for y in range(size.y)] for x in range(size.z)]
        self.model = Mesh(vertices=[], uvs=[], render_points_in_3d=True, thickness=1)
        self.texture = 'tileset'
        self.temp = Entity(parent=self, model=Mesh(), texture=self.texture, collision=False)
        self.temp.grid = [[[0 for z in range(size.x)]for y in range(size.y)] for x in range(size.z)]

        for key, value in kwargs.items():
            setattr(self, key ,value)

    def render(self):
        t = time.perf_counter()
        self.model.vertices, self.model.uvs = voxels_to_mesh(self.grid) # .035, .01
        print(time.perf_counter() - t)
        self.model.generate()


    def input(self, key):
        if key == 'f2':
            self.render_mode = 'default'
            self.render()
        if key == 'f3':
            self.render_mode = 'point'
            self.render()

        global tileset_index
        if key == 'left arrow' and tileset_index > 1:
            tileset_index -= 1
            print(tileset_index)
        if key == 'right arrow' and tileset_index < 8:
            tileset_index += 1
            print(tileset_index)


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
                neightbors = (min(e, 1) for e in neighbors)

                if neighbors == (1,1,1,1,1,1):
                    continue

                for i, e in enumerate(neighbors):
                    if not e:
                        vertices.extend([(e[0]+x, e[1]+y, e[2]+z) for e in cube_sides[i]])

                        y_offset = 0
                        y_offset += int(i==2) * 2       # top
                        y_offset += int(i not in (2,3)) * int(not u)    # sides without block above

                        # uvs.extend([e + Vec2((voxels[x][y][z]-1) / 8, y_offset/8) for e in cube_side_uvs])
                        uvs.extend([(e[0] + (voxels[x][y][z]-1)/8, e[1] + y_offset/8) for e in cube_side_uvs])

    return vertices, uvs


brush.scale = 1
brush_shape = [[[1 for z in range(int(brush.scale.x))]for y in range(int(brush.scale.y))] for x in range(int(brush.scale.z))]

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='quad', origin_y=-.5)
        self.speed = 5
        self.vertical_speed = 10

        self.mouse_rotation_speed = 40
        self.controller_rotation_speed = 80
        self.zoom_speed = 10

        self.camera_pivot = Entity(parent=self, y=.5, rotation_x=20)

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

        # block placement
        brush.position = [floor(e) for e in player.position]

        if mouse.left or held_keys['space'] or mouse.right or held_keys['gamepad a']:
            # for chunk in chunks:
            x, y, z = [int(e) for e in player.get_position(relative_to=current_chunk)]
            org_grid = deepcopy(current_chunk.grid)


            if x >= 0 and x < chunk_size.x and y >= 0 and y < chunk_size.y and z >= 0 and z < chunk_size.z:
                if mouse.left or held_keys['space'] or held_keys['gamepad a']:
                    if current_chunk.grid[x][y][z]:
                        return

                    for brush_x in range(len(brush_shape)):
                        for brush_y in range(len(brush_shape[0])):
                            for brush_z in range(len(brush_shape[0][0])):
                                if brush_shape[brush_x][brush_y][brush_z]:
                                    if is_out_of_bounds(x+brush_x, y+brush_y, z+brush_z):
                                        continue
                                    current_chunk.temp.grid[x+brush_x][y+brush_y][z+brush_z] = tileset_index

                    t = time.perf_counter()
                    current_chunk.temp.model.vertices, current_chunk.temp.model.uvs = voxels_to_mesh(current_chunk.temp.grid) # .035, .01
                    print(time.perf_counter() - t)
                    current_chunk.temp.model.generate()


                elif mouse.right or held_keys['gamepad x']:
                    for brush_x in range(len(brush_shape)):
                        for brush_y in range(len(brush_shape[0])):
                            for brush_z in range(len(brush_shape[0][0])):
                                if brush_shape[brush_x][brush_y][brush_z]:
                                    if is_out_of_bounds(x+brush_x, y+brush_y, z+brush_z):
                                        continue
                                    current_chunk.grid[x+brush_x][y+brush_y][z+brush_z] = 0

                    if not current_chunk.grid == org_grid:
                        t = time.perf_counter()
                        current_chunk.render()
                        # print(time.perf_counter() - t, 1/60)


    def input(self, key):
        if key == 'left mouse up' or key == 'gamepad a up': # apply the blocks from the temp grid
            for x in range(current_chunk.size.x):
                for y in range(current_chunk.size.y):
                    for z in range(current_chunk.size.z):
                        if current_chunk.temp.grid[x][y][z]:
                            current_chunk.grid[x][y][z] = tileset_index

            current_chunk.render()
            current_chunk.temp.grid = [[[0 for z in range(current_chunk.size.x)]for y in range(current_chunk.size.y)] for x in range(current_chunk.size.z)]
            current_chunk.temp.model.clear()
            current_chunk.temp.model.generate()


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


    def on_enable(self):
        mouse.locked = True
        brush.enabled = True

    def on_disable(self):
        mouse.locked = False
        brush.enabled = False


window.vsync = False
app = Ursina()

import noise
from noise import *
from ursina.shaders import lit_with_shadows_shader

num_chunks = 1
# num_chunks = 8
# chunks = [[Chunk(position=(x*chunk_size.x, 0, z*chunk_size.z), shader=lit_with_shadows_shader) for z in range(num_chunks)] for x in range(num_chunks)]
# current_chunk = chunks[0][0]
current_chunk = Chunk(shader=lit_with_shadows_shader)

for x in range(chunk_size.x):
    for z in range(chunk_size.z):
        for y in range(1):
            current_chunk.grid[x][y][z] = tileset_index

for z in range(chunk_size.z):
    for x in range(chunk_size.x):
        noise = pnoise2(x/chunk_size.x, z/chunk_size.z, octaves=3, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)
        noise = int((noise+.5)*chunk_size.y)
        for y in range(noise):
            current_chunk.grid[x][y][z] = tileset_index

current_chunk.render()

def is_out_of_bounds(x, y, z):
    return x < 0 or x >= current_chunk.size.x or y < 0 or y >= current_chunk.size.y or z < 0 or z >= current_chunk.size.z


from ursina.prefabs.file_browser import FileBrowser
from ursina.prefabs.file_browser_save import FileBrowserSave
file_browser =      FileBrowser(start_path=Path('.'), file_types=('.json'), enabled=False, ignore_paused=True)
file_browser_save = FileBrowserSave(file_types=('.json'), enabled=False, ignore_paused=True)
current_file = None

def on_submit(value):
    for path in value:
        print('---', path)
        save()

file_browser_save.on_submit = on_submit
file_browser_save.on_enable = Func(setattr, mouse, 'locked', False)


def save_current_file():
    if not current_file:
        print('error: trying to save() when current_file is None, use save_as() instead')
        return

    with open(current_file, 'w') as file:
        json.dump(current_chunk.grid, file)


def save_as(path):
    with open(path, 'w') as file:
        json.dump(current_chunk.grid, file)


def load():
    with open('test.json', 'r') as file:
        current_chunk.grid = json.load(file)
        current_chunk.render()

current_file = None
def input(key):
    global current_file
    if held_keys['control'] and key == 's':
        if current_file:
            save_current_file()
        elif not file_browser_save.enabled:
            file_browser_save.enabled = True

    if held_keys['control'] and key == 'l':
        current_file = Path('test.json')
        load()



# 125 641 blocks
player = Player(position=Vec3(num_chunks/2*chunk_size.x,0,num_chunks/2*chunk_size.z), model=None)
from ursina.shaders import unlit_shader

class MouseControls(Entity):
    def __init__(self, **kwargs):
        self.editor_camera = EditorCamera(parent=self, enabled=False, position=Vec3(num_chunks/2*chunk_size.x,0,num_chunks/2*chunk_size.z), rotation_x=45, zoom_speed=2)
        super().__init__(position=Vec3(chunk_size.x/2, 0, chunk_size.z/2), **kwargs)
        self.cursor = Entity(parent=self, model='quad', color=color.lime, unlit=True)


    def update(self):
        if not mouse.hovered_entity == current_chunk or not mouse.world_point:
            self.cursor.enabled = False
            return
        else:
            self.cursor.enabled = True
            self.cursor.world_position = Vec3(*[int(e) for e in mouse.world_point-(mouse.normal/2)]) + Vec3(.5,.5,.5) + (mouse.normal*.501)
            self.cursor.look_at(self.cursor.position + mouse.world_normal, axis='back')

    def input(self, key):
        if mouse.hovered_entity == current_chunk and mouse.world_point:
            if key == 'left mouse down':
                self.build(1, dig=held_keys['alt'])

            if key in '123456789':
                self.build(int(key), dig=held_keys['alt'], stop_on_hit=False)


    def build(self, amount=1, dig=False, stop_on_hit=False):
        start_pos = mouse.point-(mouse.normal/2)

        for i in range(amount):
            x, y, z = [int(e) for e in start_pos + (mouse.normal * (i+1-int(dig)) * (1,-1)[int(dig)])]

            if is_out_of_bounds(x, y, z): # make sure it's inside the chunk
                break

            if stop_on_hit and current_chunk.grid[x][y][z] == int(not dig):
                break

            current_chunk.grid[x][y][z] = int(not dig) * tileset_index

        current_chunk.render()
        current_chunk.collider = 'mesh'


    def on_enable(self):
        camera.z = -30
        self.editor_camera.enabled = True
        current_chunk.collider = 'mesh'
        mouse.traverse_target = scene

    def on_disable(self):
        self.editor_camera.enabled = False
        mouse.traverse_target = None


mouse_controls = MouseControls()


state_handler = Animator({
    'mouse_controls' : mouse_controls,
    'controller' : player,
})
class PlayerToggler(Entity):
    def input(self, key):
        if key == 'tab':
            if state_handler.state == 'controller':
                state_handler.state = 'mouse_controls'
            else:
                state_handler.state = 'controller'

PlayerToggler()


sky = Sky()
Entity(parent=render, model='plane', scale=9999, color='#b8523b')

DirectionalLight(rotation_x=30)

app.run()
