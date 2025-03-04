import bpy
from bpy.props import StringProperty, BoolProperty # type: ignore

class DATAMOSH_PT_panel(bpy.types.Panel):
    bl_label = "Datamosh"
    bl_idname = "DATAMOSH_PT_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Datamosh'

    def draw(self, context):
        layout = self.layout
        layout.operator("datamosh.run_datamosh")
        layout.operator("datamosh.get_start_frames")

        scene = context.scene
        layout.prop(scene, "datamosh_start_frames")
        layout.prop(scene, "datamosh_start_points")
        layout.prop(scene, "datamosh_end_points")

def register():
    bpy.utils.register_class(DATAMOSH_PT_panel)
    bpy.types.Scene.datamosh_start_frames = StringProperty(
        name="Transition Frames",
        description="Start frames of movie sequences in the sequencer",
        default=""
    )
    bpy.types.Scene.datamosh_start_points = StringProperty(
        name="Start Frames",
        description="Start points for datamoshing",
        default=""
    )
    bpy.types.Scene.datamosh_end_points = StringProperty(
        name="End Frames",
        description="End points for datamoshing",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(DATAMOSH_PT_panel)
    del bpy.types.Scene.datamosh_start_frames
    del bpy.types.Scene.datamosh_start_points
    del bpy.types.Scene.datamosh_end_points