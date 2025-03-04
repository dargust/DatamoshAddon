bl_info = {
    "name": "Datamosh Video",
    "author": "Dan Argust",
    "version": (0, 1, 10),
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
    bpy.utils.register_class(operator.DATAMOSH_OT_run_datamosh)
    bpy.utils.register_class(panel.DATAMOSH_PT_panel)

def unregister():
    bpy.utils.unregister_class(operator.DATAMOSH_OT_run_datamosh)
    bpy.utils.unregister_class(panel.DATAMOSH_PT_panel)