bl_info = {
    "name": "Datamosh Video",
    "author": "Dan Argust",
    "version": (0, 1, 19),
    "blender": (2, 82, 0),
    "category": "Video Tools",
}

if "bpy" in locals():
    import importlib as imp
    imp.reload(operator)
    imp.reload(panel)
else:
    from . import operator
    from . import panel

import bpy

def register():
    operator.register()
    panel.register()

def unregister():
    operator.unregister()
    panel.unregister()