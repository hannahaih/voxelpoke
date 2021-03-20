from ursina import *




#
# # class E(Entity):
# #     getattr_translation = {
# #         'p' : 'position',
# #         'r' : 'rotation',
# #         's' : 'scale',
# #         'm' : 'model',
# #         'c' : 'color',
# #         'coll' : 'collider',
# #     }
# #     setattr_translation = {value:key for (key, value) in getattr_translation.items()}
# #
# #     def __getattr__(self, name):
# #         if name in E.getattr_translation:
# #             name = E.getattr_translation[name]
# #
# #         return getattr(super(), name)
# #
# #     def __setattr__(self, name, value):
# #         if name in E.setattr_translation:
# #             name = E.setattr_translation[name]
# #
# #             setattr(super(), name, value)
#
app = Ursina()
e = Entity(model='cube', texture='white_cube', texture_scale=(16,16), scale=16, collider='box')
e.flip_faces()
from ursina.prefabs.first_person_controller import FirstPersonController
FirstPersonController()
# # Entity(model='cube', collider='')
#
# # e = E(m='cube')
# # print(e.p)
# Entity(model='cube', position=Vec3(0,0,0)+Vec3(-.5,-0,-.5), scale=3, origin=(-.5,-.5,-.5), collider='box', color=rgb(1,0,0,.1), visible=True)
# # Entity(model='cube')
# EditorCamera()
app.run()
