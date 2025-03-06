import bpy
from bpy.props import StringProperty

class DATAMOSH_PT_panel(bpy.types.Panel):
    bl_label = "Datamosh"
    bl_idname = "DATAMOSH_PT_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Datamosh'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sequence_editor = scene.sequence_editor

        has_sequences = sequence_editor and len(sequence_editor.sequences_all) > 0
        has_valid_inputs = bool(scene.datamosh_start_frames.strip()) and bool(scene.datamosh_start_points.strip()) and bool(scene.datamosh_end_points.strip())

        if (has_sequences and has_valid_inputs):
            layout.operator("datamosh.run_datamosh", text="Run Datamosh")

        layout.operator("datamosh.get_start_frames", text="Get Start Frames")

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

if __name__ == "__main__":
    register()