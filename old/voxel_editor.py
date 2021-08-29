from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from grid_to_cubes import grid_to_cubes
import noise
from noise import *


window.vsync = False
app = Ursina()

# colliders = [[[Entity(collider='box', add_to_scene_entities=False) for z in range(size)]for y in range(size)] for x in range(size)]
class Voxel(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', collider='box', texture='white_cube')
        self.add_to_scene_entities = False
        for key, value in kwargs.items():
            setattr(self, key ,value)

# tris = ((0,1,5,4), )
# uvs = [cube_verts[i].xy+Vec2(.5,.5) for i in tris[0]]
# voxel.model = Mesh(vertices=cube_verts, triangles=tris, uvs=uvs)
cube_verts = [
    Vec3(-.5,-.5,-.5), Vec3(.5,-.5,-.5), Vec3(.5,-.5,.5), Vec3(-.5,-.5,.5),
    Vec3(-.5,.5,-.5), Vec3(.5,.5,-.5), Vec3(.5,.5,.5), Vec3(-.5,.5,.5)
]
cube_uvs = ((0,0), (1,0), (1,1), (0,1))

tileset = load_blender_scene('tileset', models_only=True, reload=False)
models = {
    '000000' : None,
    # '111111' : 'cube',
    '110111' : Mesh(vertices=[cube_verts[i] for i in (4,5,6, 4,6,7)]), # floor
    '111011' : Mesh(vertices=[cube_verts[i] for i in (3,2,1, 3,1,0)]), # ceiling
    '110011' : Mesh(vertices=[cube_verts[i] for i in (4,5,6, 4,6,7, 3,2,1, 3,1,0)]), # floor and ceiling

    '111110' : Mesh(vertices=[cube_verts[i] for i in (0,1,5, 0,5,4)]), # wall front
    '111101' : Mesh(vertices=[cube_verts[i] for i in (2,3,7, 2,7,6)]), # wall back
    '111100' : Mesh(vertices=[cube_verts[i] for i in (0,1,5, 0,5,4, 2,3,7, 2,7,6)]), # wall front and back

    '011111' : Mesh(vertices=[cube_verts[i] for i in (1,2,6, 1,6,5)]), # wall right
    '101111' : Mesh(vertices=[cube_verts[i] for i in (3,0,4, 3,4,7)]), # wall left
    '001111' : Mesh(vertices=[cube_verts[i] for i in (1,2,6, 1,6,5, 3,0,4, 3,4,7)]), # wall left and right

    '000100' : tileset['roof_2'], #spire
    # 'ceiling' : 'plane',
    # 'ground_and_ceiling' : 'plane',
    # 'wall_back' : 'quad',
    # 'wall_front_back' : 'quad',
    # 'wall_left' : 'quad',w
    # 'wall_right' : 'quad',
    # 'wall_left_right' : 'quad',

}
for key, value in models.items():
    if value:
        models[key].uvs = ((0,0), (1,0), (1,1), (0,0), (1,1), (0,1)) * (len(value.vertices) //6)
        models[key].generate()



class Chunk(Entity):
    build_keys = ['left mouse down', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    cursor = Entity(model=Quad(), origin_z=.5, color=color.lime, alpha=.3, always_on_top=True)


    def __init__(self, **kwargs):
        super().__init__()
        self.size = 16
        self.position = -Vec3(self.size, 0, self.size)/2
        self.grid = [[[0 for z in range(self.size)]for y in range(self.size)] for x in range(self.size)]
        # for x in range(self.size):
        #     for z in range(self.size):
        #         self.grid[x][0][z] = Voxel(parent=self, position=Vec3(x,0,z), color=color.color(0,0,.5))
        # for x in range(2,5):
        #     for z in range(2,5):
        #         for y in range(1,4):
        #             self.grid[x][y][z] = Voxel(parent=self, position=Vec3(x,y,z), color=color.color(0,0,.5))



        for z in range(self.size):
            for x in range(self.size):
                noise = pnoise2(x/self.size, z/self.size, octaves=3, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)
                noise = int((noise+.5)*self.size)
                for y in range(noise):
                    self.grid[x][y][z] = Voxel(parent=self, position=Vec3(x,y,z), color=color.color(0,0,.5))




        self.scale=2
        self.vertical_only = False

        self.edit_mode_button = Button(
            parent=self,
            model='cube',
            scale=.5,
            position=Vec3(self.size,self.size/2,self.size)/2,
            text='edit',
            highlight_color=color.azure,
            enabled=False,
            always_on_top=True,
            on_click=Func(setattr, self, 'edit_mode', True),
            )
        self.children.remove(self.edit_mode_button)
        self.edit_mode = True
        self.colliders = []
        self.texture = 'white_cube'
        self.color = color.pink
        self.get_shape_for_all()

        for key, value in kwargs.items():
            setattr(self, key ,value)



    def update(self):
        # if not mouse.hovered_entity or not isinstance(mouse.hovered_entity, Voxel):
        if not mouse.hovered_entity or not mouse.hovered_entity in self.colliders or mouse.normal == Vec3(0,0,0):
            return

        Chunk.cursor.world_position = mouse.world_point - (mouse.normal/2)
        Chunk.cursor.x = math.floor(Chunk.cursor.x+.5)
        Chunk.cursor.y = math.floor(Chunk.cursor.y+.5)
        Chunk.cursor.z = math.floor(Chunk.cursor.z+.5)

        direction = mouse.normal
        if self.vertical_only:
            direction = Vec3(0,1,0)

        Chunk.cursor.look_at(Chunk.cursor.position + direction, axis='back')



    def input(self, key):
        if key == 'tab':
            self.edit_mode = not self.edit_mode


        if not mouse.hovered_entity or not mouse.hovered_entity in self.colliders:
            return

        if held_keys['alt'] and key == 'left mouse down' or not held_keys['shift'] and key == 'x':
            self.dig()
            return

        # if key == 'right mouse up' and sum([abs(e) for e in mouse.delta_drag]) < .01:
        #     self.dig()
        #     return


        if key == 'f':
            self.build(amount=self.size, stop_on_hit=True)

        # try to create new voxel
        if key in Chunk.build_keys and not held_keys['shift']:
            self.build(amount=max(1, Chunk.build_keys.index(key)), stop_on_hit=False)

        if held_keys['control'] and key == 'r':
            self.reset()

        # dig
        if held_keys['shift'] and key in Chunk.build_keys + ['x', ]:
            if key == 'x':
                self.dig(amount=self.size, stop_on_air=not held_keys['control'])
            else: # dig specific amount
                self.dig(amount=max(1, Chunk.build_keys.index(key)), stop_on_air=False)

        if key == 'v':
            self.vertical_only = not self.vertical_only


        if key == 'u':
            self.get_shape_for_all()

        if held_keys['control'] and key == 's':
            self.save()


    def build(self, amount=1, stop_on_hit=True):
        # print('build', 1, amount+1)
        for j in range(1, amount+1):
            # target_pos = mouse.hovered_entity.position + (Chunk.cursor.back * j)
            target_pos = Chunk.cursor.get_position(relative_to=self) + (Chunk.cursor.back * j / self.scale_x)

            # make sure it's inside the chunk
            for i in range(3):
                if target_pos[i] < 0 or target_pos[i] >= self.size:
                    print('out of bounds')
                    self.get_shape_for_all()
                    return
            # skip it there's already a voxel at position
            if self.grid[int(target_pos.x)][int(target_pos.y)][int(target_pos.z)]:
                if stop_on_hit:
                    self.get_shape_for_all()
                    return
                print('skip:', target_pos)
                continue

            # print(1-(target_pos.z/size))
            voxel = Voxel(parent=self, position=target_pos)
            self.grid[int(target_pos.x)][int(target_pos.y)][int(target_pos.z)] = voxel

        self.get_shape_for_all()



    def get_shape(self, voxel):
        directions = (Vec3(1,0,0), Vec3(-1,0,0), Vec3(0,1,0), Vec3(0,-1,0), Vec3(0,0,1), Vec3(0,0,-1))
        neighbour_info = [0,0,0,0,0,0]

        for i, dir in enumerate(directions):
            neighbour_pos = voxel.position + dir

            if (neighbour_pos.x < 0 or neighbour_pos.y < 0 or neighbour_pos.z < 0
            or neighbour_pos.x >= self.size or neighbour_pos.y >= self.size or neighbour_pos.z >= self.size):  # at the edge of chunk
                neighbour_info[i] = 0
                continue
            neighbour_info[i] = int(bool(self.grid[int(neighbour_pos.x)][int(neighbour_pos.y)][int(neighbour_pos.z)]))

        # print(neighbour_info)

        id = ''.join([str(e) for e in neighbour_info])
        # print(id)
        if id in models:
            voxel.model = copy(models[id])
        else:
            voxel.model = 'cube'


    def get_shape_for_all(self):
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    block = self.grid[x][y][z]
                    if block:
                        block.color = color.color(0,0, .75 + (y/self.size*.5))
                        self.get_shape(block)

        # make colliders
        for e in self.colliders:
            destroy(e)
        self.colliders.clear()

        for cube_data in grid_to_cubes(self.grid, self.size, self.size, self.size):
            pos, scale = cube_data
            collider = Entity(parent=self, model='cube', position=Vec3(*pos)+Vec3(-.5,-.5,-.5), scale=scale, origin=(-.5,-.5,-.5), collider='box', color=color.red, visible=False)
            self.children.remove(collider)
            self.colliders.append(collider)



    def dig(self, amount=1, stop_on_air=True):
        print('stop_on_air:', stop_on_air)
        # start_pos = mouse.hovered_entity.position
        start_pos = Chunk.cursor.get_position(relative_to=self)
        direction = -Chunk.cursor.back

        for j in range(amount):
            target_pos = start_pos + (direction * j)

            # make sure it's inside the chunk
            for i in range(3):
                if target_pos[i] < 0 or target_pos[i] >= self.size:
                    print('out of bounds')
                    return

            # skip it there's already a voxel at position
            if not self.grid[int(target_pos.x)][int(target_pos.y)][int(target_pos.z)]:
                if stop_on_air:
                    print('stop on air')
                    return
                print('skip:', target_pos)
                continue

            destroy(self.grid[int(target_pos.x)][int(target_pos.y)][int(target_pos.z)])
            self.grid[int(target_pos.x)][int(target_pos.y)][int(target_pos.z)] = 0
            self.get_shape_for_all()


    def reset(self):
        print('reset')
        for e in self.children:
            destroy(e)

        self.grid = [[[0 for z in range(self.size)]for y in range(self.size)] for x in range(self.size)]
        for x in range(self.size):
            for z in range(self.size):
                self.grid[x][0][z] = Voxel(parent=self, position=Vec3(x,0,z))

        self.get_shape_for_all()


    def save(self):
        data = [[[0 for z in range(self.size)]for y in range(self.size)] for x in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    data[x][y][z] = int(bool(self.grid[x][y][z]))

        print(data)


    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        print('exit edit mode:', value)
        self._edit_mode = value
        self.edit_mode_button.enabled = not value
        Chunk.cursor.enabled = value

        if value:
            Chunk.cursor.parent = self
            self.model = None
            for x in range(self.size):
                for y in range(self.size):
                    for z in range(self.size):
                        if self.grid[x][y][z]:
                            self.grid[x][y][z].enabled = True
                        # print(self.grid[x][y][z])

        else:
            print('exit edit mode')
            self.combine(auto_destroy=False, ignore=[self.edit_mode_button, ])
            for voxel in self.children:
                voxel.enabled = False




chunk = Chunk()

# from ursina.shaders.ssao_3 import ssao_shader
# camera.shader = ssao_shader
camera.fov = 30
camera.z = -80
# camera.editor_position = Vec3(0,0,-32)
# player = FirstPersonController(gravity=0)
EditorCamera(position=(8,0,8), rotation_x = 30)
app.run()
