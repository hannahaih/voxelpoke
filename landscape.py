from ursina import *



app = Ursina()


# Entity(model='plane', scale=500, texture='landscape')
# Sky()
# water = Entity(model='plane', scale=9999, color='#2199d1', y=-10)
# EditorCamera()
# camera.world_position = Vec3(-28.4396, 8.86357, -101.827)
#
# def input(key):
#     if key == 'space':
#         print(camera.world_position)
window.color = color._64
Entity(model='quad', parent=camera.ui, texture='shore', scale=(camera.aspect_ratio,1), color=color.dark_gray)
InputField(highlight_color=color.black)
InputField(highlight_color=color.black, y=-.06)
Button(text='Login', color=color.azure, y=-.15, scale=(.25,.05))

app.run()
