from ursina import *
from pprint import pprint


# override the built in round to easily round Vec3 and tuples/lists
builtin_round = round
def round(value, decimals=0):
    if isinstance(value, Vec3):
        return Vec3(builtin_round(value[0],decimals), builtin_round(value[1],decimals), builtin_round(value[2],decimals))

    if isinstance(value, list):
        return [builtin_round(e,decimals) for e in value]

    if isinstance(value, tuple):
        return tuple(builtin_round(e,decimals) for e in value)

    return builtin_round(value, decimals)


app = Ursina()

# make hexagon
w = 3.46
verts = list()
points = list()

# bottom part of the hexagon
for y in range(1, 6):
    for x in range(y):
        points.append(Vec3((x+.5-(y/2))*w, y-1, 0))
        verts.extend((
            Vec3((x+.5-(y/2))*w, y-1, 0), Vec3((x+1-(y/2))*w, y, 0), Vec3((x+.5-(y/2))*w, y+1, 0),
            Vec3((x+.5-(y/2))*w, y-1, 0), Vec3((x+.5-(y/2))*w, y+1, 0), Vec3((x-(y/2))*w, y, 0),
        ))

# middle part of the hexagon
for y in range(1, 10):
    length = 6
    offset = .5
    if y%2 == 0:
        length -= 1
        offset = 1

    for x in range(length):
        points.append(Vec3(((x+offset-(6/2))*w), y+4, 0))
        if x == 0 and y < 10 and y%2 != 0:
            verts.extend((
                Vec3(((x+offset-(6/2))*w), y+4, 0), Vec3(((x+offset+.5-(6/2))*w), y+5, 0), Vec3(((x+offset-(6/2))*w), y+6, 0),
            ))
        elif x == length-1 and y < 10 and y%2 != 0:
            verts.extend((
            Vec3(((x+offset-(6/2))*w), y+4, 0), Vec3(((x+offset-(6/2))*w), y+6, 0), Vec3(((x+offset-.5-(6/2))*w), y+5, 0),
            ))

        else:
            verts.extend((
                Vec3(((x+offset-(6/2))*w), y+4, 0), Vec3(((x+offset+.5-(6/2))*w), y+5, 0), Vec3(((x+offset-(6/2))*w), y+6, 0),
                Vec3(((x+offset-(6/2))*w), y+4, 0), Vec3(((x+offset-(6/2))*w), y+6, 0), Vec3(((x+offset-.5-(6/2))*w), y+5, 0),
            ))

# top part of the hexagon
for y in range(5, 0, -1):
    for x in range(y):
        points.append(Vec3((x+.5-(y/2))*w, 19-y, 0))
        verts.extend((
            Vec3((x+.5-(y/2))*w, 19-y, 0), Vec3((x+1-(y/2))*w, 20-y, 0), Vec3((x+.5-(y/2))*w, 21-y, 0),
            Vec3((x+.5-(y/2))*w, 19-y, 0), Vec3((x+.5-(y/2))*w, 21-y, 0), Vec3((x-(y/2))*w, 20-y, 0),
        ))

outline_lines = (
    (Vec3(0*w, 0, 0)),
    Vec3(2.5*w, 5, 0),
    Vec3(2.5*w, 15, 0),
    Vec3(0*w, 20, 0),
    Vec3(-2.5*w, 15, 0),
    Vec3(-2.5*w, 5, 0),
    )
outline_lines = (
    (outline_lines[0], outline_lines[1]),
    (outline_lines[1], outline_lines[2]),
    (outline_lines[2], outline_lines[3]),
    (outline_lines[3], outline_lines[4]),
    (outline_lines[4], outline_lines[5]),
    (outline_lines[5], outline_lines[0]),
)
outline_points = list()
for line in outline_lines:
    segments = 10
    for j in range(segments):
        p = lerp(line[0], line[1], j/segments)
        p = tuple(round(p, 3))
        outline_points.append(p)


outline_mesh = Entity(model=Mesh(vertices=outline_points, mode='point', thickness=3), color=color.cyan, z=-2)
model = Mesh(verts, mode='triangle')
hexagon_points = Entity(model=Mesh(vertices=points, mode='point', thickness=5))
hexagon = Entity(model=model, color=color.white33)


new_verts = list()
subdivided_quads = list()
new_mesh = Entity(model=Mesh(vertices=new_verts, thickness=10, mode='triangle'), color=color.orange, z=-.1)
new_mesh_2 = Entity(model=Mesh(vertices=subdivided_quads, mode='triangle'), color=color.dark_gray.tint(-.025), z=-.2)
# new_mesh_3 = Entity(model=Mesh(vertices=subdivided_quads, mode='line'), color=color.lime, z=-.3)

tris = list()
for i in range(0, len(verts), 3):
    tris.append((verts[i+0], verts[i+1], verts[i+2]))

# pprint(tris)
points = dict()
random.seed(17)
grid_quads = list()
# random.seed(26)

def connect():
    # print(len(tris))
    current_tri = random.choice(tris)

    connections = list()
    for t in tris:
        if len(set(tuple(current_tri) + tuple(t))) == 4: # get pairs with only 4 unique points, they are valid neigbors
            connections.append(t)

    if not connections:
        print('no valid connections found')
        return False

    random_neighbor = random.choice(connections)
    current_center = (current_tri[0] + current_tri[1] + current_tri[2]) / 3
    neighbor_center = (random_neighbor[0] + random_neighbor[1] + random_neighbor[2]) / 3
    center = (current_center + neighbor_center) / 2

    quad = set(current_tri + random_neighbor)

    if current_center[1] == neighbor_center[1]:  # flat ones <>
        s, n = [e for e in quad if not e[1] == center[1]]
        if s[1] > n[1]:
            s, n = n, s
        w, e = [e for e in quad if not e in (s,n)]
        if w[0] > e[0]:
            w, e = e, w

    elif current_center[0] < neighbor_center[0]:
        if current_center[1] < neighbor_center[1]:  # right up
            s,e,n,w = current_tri[0], current_tri[1], random_neighbor[1], current_tri[2]
        else:   # right down
            s,e,n,w = current_tri[0], random_neighbor[0], current_tri[1], current_tri[2]
    else:   # left up
        if current_center[1] < neighbor_center[1]:
            s,e,n,w = current_tri[0], current_tri[1], random_neighbor[2], current_tri[2]
        else:   # left down
            s,e,n,w = current_tri[0], current_tri[1], current_tri[2], random_neighbor[0]

    se,ne,nw,sw = (s+e)/2, (n+e)/2, (n+w)/2, (s+w)/2

    cc_shape = (s,se,e,ne,n,nw,w,sw) # points in counter clockwise order
    cc_shape = [round(e, 3) for e in cc_shape]
    betweens = (cc_shape[1], cc_shape[3], cc_shape[5], cc_shape[7])

    rounded_center = round(center, 3)
    if not str(rounded_center) in points:
        points[str(rounded_center)] = betweens

    for i, p in enumerate(cc_shape):
        name = str(p)
        if not name in points:
            points[name] = list()

        prev = cc_shape[i-1]
        if i == len(cc_shape)-1:
            next = cc_shape[0]
        else:
            next = cc_shape[i+1]

        points[name].append(Vec3(prev))
        points[name].append(Vec3(next))

        if p in betweens:
            points[name].append(Vec3(*rounded_center))


    # visuals
    quads = ((center,se,e,ne), (center,ne,n,nw), (center,nw,w,sw), (center,sw,s,se))
    grid_quads.extend(quads)
    for q in quads:
        a,b,c,d = q
        # c = (a+b+c+d) / 4
        # a,b,c,d = [lerp(c, e, .95) for e in q]
        new_mesh_2.model.vertices.extend((a,b,c, a,c,d))

    new_mesh_2.model.generate()
    # new_verts.extend(current_tri)
    # new_verts.extend(random_neighbor)
    new_mesh.model.vertices.extend([lerp(center, v, .9) for v in current_tri])
    new_mesh.model.vertices.extend([lerp(center, v, .9) for v in random_neighbor])
    new_mesh.model.generate()

    tris.remove(current_tri)
    tris.remove(random_neighbor)
    return True


def subdivide_triangles():
    for current_tri in tris:
        center = (current_tri[0] + current_tri[1] + current_tri[2]) / 3

        a, b, c = current_tri
        ab, bc, ca = (a+b)/2, (b+c)/2, (c+a)/2

        cc_shape = (a,ab,b,bc,c,ca) # points in counter clockwise order
        cc_shape = [round(e,3) for e in cc_shape]
        betweens = (cc_shape[1], cc_shape[3], cc_shape[5])
        rounded_center = round(center, 3)
        if not str(rounded_center) in points:
            points[str(rounded_center)] = betweens

        for i, p in enumerate(cc_shape):
            name = str(p)
            if not name in points:
                points[name] = list()

            prev = cc_shape[i-1]
            if i == len(cc_shape)-1:
                next = cc_shape[0]
            else:
                next = cc_shape[i+1]

            points[name].append(Vec3(prev))
            points[name].append(Vec3(next))

            if p in betweens:
                points[name].append(Vec3(*rounded_center))

        # visuals
        quads = ((center,ab,b,bc), (center,bc,c,ca), (center,ca,a,ab))
        for q in quads:
            a,b,c,d = q
            c = (a+b+c+d) / 4
            a,b,c,d = [lerp(c, e, .95) for e in q]
            new_mesh_2.model.vertices.extend((a,b,c, a,c,d))

        new_mesh.model.vertices.extend([lerp(center, v, .9) for v in current_tri])

    new_mesh.model.generate()
    new_mesh_2.model.generate()

    tris.remove(current_tri)


def smooth():
    print('smooth')
    quad_ids = list()
    for q in grid_quads:
        quad_ids.append([new_mesh_2.model.vertices.index(pos) for pos in q])
        # for pos in q:
            # print(new_mesh_2.model.vertices.index(pos))
        # print(q)
    # quad_ids = list()
    # for i in range(0, len(new_mesh.model.vertices)-4, 4):
    #     # print('---', [round(new_mesh.model.vertices[i+j], 3) for j in range(4)])
    #     quad = [new_mesh.model.vertices[i+j] for j in range(4)]
    #     quad = [new_mesh.model.vertices.index(pos) for pos in quad]
    #     # for pos in q:
    #     #     print(new_mesh.model.vertices.index(pos))
    #         # print(new_mesh.model.vertices.index[pos])
    #     print('...', quad, type(quad))
    #     quad_ids.append(quad)

    print(max(quad_ids))
    # Entity(model=Mesh(new_mesh_2.model.vertices, triangles=quad_ids), color=color.green, z=-5)

    vertices = [eval(e.replace('LVector3f', '')) for e in points.keys()]
    print('len vertices:', len(vertices))
    lines = list()


    for key, value in points.items():
        a = vertices.index(eval(key.replace('LVector3f', '')))
        for pos in value:
            pos = round(tuple(pos),3)
            # print(pos)
            b = vertices.index(pos)
            if not (b,a) in lines:
                lines.append((a,b))

    connections = list()
    for i, v in enumerate(vertices):
        _lines = [l for l in lines if i in l]
        neighbors = list()

        for l in _lines:
            neighbors.extend([e for e in l if not e == i])

        connections.append(tuple(set(neighbors)))

    print(connections)
    relaxed_verts = relax(vertices, connections)
    # relaxed_verts = vertices
    # relaxed_verts = relax(relaxed_verts, connections)
    # render
    new_mesh_2.enabled = False
    new_mesh.enabled = False

    # point_mesh = Entity(model=Mesh(vertices=list(), mode='point', thickness=5), z=-1, color=color.orange)

    for i, neighbors in enumerate(connections):
        neighbor_positions = [relaxed_verts[e] for e in neighbors]
        neighbor_positions = [Vec3(*e) for e in neighbor_positions]

        # point_mesh.model.vertices.append(relaxed_verts[i])

        lines_mesh = Entity(model=Mesh(vertices=list(), mode='line', thickness=1), color=color.black, z=-1)
        for pos in neighbor_positions:
            lines_mesh.model.vertices.extend((relaxed_verts[i], pos))

        lines_mesh.model.generate()

    # point_mesh.model.generate()
    print('finished')


def relax(points, connections):
    relaxed_verts = list()
    for i, neighbors in enumerate(connections):
        neighbor_positions = [points[e] for e in neighbors]
        neighbor_positions = [Vec3(*e) for e in neighbor_positions]

        mean = neighbor_positions[0]
        for np in neighbor_positions[1:]:
            mean += np

        mean /= len(neighbor_positions)


        if points[i] in outline_points:
            # Entity(model='quad', scale=.4, color=color.pink, position=points[i], z=-3)
            relaxed_verts.append(points[i])
            continue

        relaxed_verts.append(mean)

    return relaxed_verts


def connect_randomly():
    misses = 0
    while misses < 16:
        if connect() == False:
            misses += 1

    print('finished')

# # animate
# s = Sequence(Wait(2))
# for i in range(0, len(verts)+3, 3):
#     s.append(Func(setattr, model, 'vertices', verts[:i]))
#     s.append(Func(model.generate))
#     s.append(Wait(.025))
#
# s.start()
# subdivide each quad
misses = 0
def input(key):
    global misses
    if key == 'space' or key == 'space hold':
        connect()


    if key == 'r':
        if misses < 16:
            if connect() == False:
                misses += 1

            connect_randomly()
            connect_randomly()
        # else:
        #     subdivide_triangles()


    if key == 't':
        subdivide_triangles()
        return
        s = Sequence()
        new_mesh_2.model.vertices = ((0,0,0),(0,0,0),(0,0,0))
        new_mesh_2.model.generate()
        for i in range(0, len(subdivided_quads)+6, 6):
            s.append(Func(setattr, new_mesh_2.model, 'vertices', subdivided_quads[:i]))
            s.append(Func(new_mesh_2.model.generate))
            s.append(Wait(.0125))

        s.start()

    if key == 's':
        smooth()


# window.display_mode = 'wireframe'

camera.orthographic = True
camera.fov = 30
camera.y = 10
# window.size *= .75
# EditorCamera()

app.run()
