import bpy # type: ignore
import os
import subprocess
from bpy.props import StringProperty, BoolProperty # type: ignore
from bpy.types import Operator, Panel # type: ignore
from .parse_raw_avi import convert_to_avi, extract_avi_data, create_datamoshed_avi

class DATAMOSH_OT_run_datamosh(bpy.types.Operator):
    bl_idname = "datamosh.run_datamosh"
    bl_label = "Run Datamosh"
    bl_description = "Run the datamoshing script on the rendered video"

    def execute(self, context):
        scene = context.scene
        rendered_video = bpy.path.abspath(scene.render.filepath)

        if not os.path.exists(rendered_video):
            self.report({'ERROR'}, "Rendered video file does not exist.")
            return {'CANCELLED'}
        print(f"Attempting to datamosh: {rendered_video}")
        input_file = rendered_video
        temp_file = os.path.splitext(input_file)[0] + "_temp.avi"
        output_file = os.path.splitext(input_file)[0] + "_glitched.avi"

        sequence_editor = scene.sequence_editor
        if not sequence_editor:
            self.report({'ERROR'}, "No sequence editor found in the current scene.")
            return {'CANCELLED'}

        start_frames = [int(x) for x in scene.datamosh_start_frames.split(',')]
        start_points = [int(x) for x in scene.datamosh_start_points.split(',')]
        end_points = [int(x) for x in scene.datamosh_end_points.split(',')]

        print(f"Movie clip start frames: {start_frames}")

        convert_to_avi(input_file, temp_file)
        avi_data = extract_avi_data(temp_file)
        create_datamoshed_avi(avi_data, temp_file, output_file, start_at=start_points, end_at=end_points, duplicated_p_frames=0, transition_frames=start_frames)
        self.report({'INFO'}, "Datamoshing complete")

        # Store the list of sequences before adding the new movie strip
        sequences_before = set(sequence_editor.sequences_all)

        # Add the output_file as a new movie sequence to the timeline
        bpy.ops.sequencer.movie_strip_add(filepath=output_file, frame_start=1)

        # Store the list of sequences after adding the new movie strip
        sequences_after = set(sequence_editor.sequences_all)

        # Identify the newly added sequence
        new_sequence = (sequences_after - sequences_before).pop()

        # Set the proxy settings for the newly added movie strip
        if new_sequence.type == 'MOVIE':
            new_sequence.use_proxy = False
            new_sequence.proxy.build_25 = False
            new_sequence.proxy.build_50 = False
            new_sequence.proxy.build_75 = False
            new_sequence.proxy.build_100 = False
            new_sequence.proxy.quality = 50

        return {'FINISHED'}

class DATAMOSH_OT_get_start_frames(bpy.types.Operator):
    bl_idname = "datamosh.get_start_frames"
    bl_label = "Get Start Frames"
    bl_description = "Get the start frames of all movie sequences in the sequencer"

    def execute(self, context):
        scene = context.scene
        sequence_editor = scene.sequence_editor

        if not sequence_editor:
            self.report({'ERROR'}, "No sequence editor found in the current scene.")
            return {'CANCELLED'}

        start_frames = []
        for sequence in sequence_editor.sequences_all:
            if sequence.type == 'MOVIE':
                frame = int(sequence.frame_final_start) - 1
                if frame > 11:
                    start_frames.append(frame)

        scene.datamosh_start_frames = ','.join(map(str, start_frames))
        scene.datamosh_start_points = ','.join(map(str, [frame - 10 for frame in start_frames]))
        scene.datamosh_end_points = ','.join(map(str, [frame + 60 for frame in start_frames]))
        self.report({'INFO'}, f"Start frames: {start_frames}")
        self.report({'INFO'}, f"Start points: {scene.datamosh_start_points}")
        self.report({'INFO'}, f"End points: {scene.datamosh_end_points}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(DATAMOSH_OT_run_datamosh)
    bpy.utils.register_class(DATAMOSH_OT_get_start_frames)

def unregister():
    bpy.utils.unregister_class(DATAMOSH_OT_run_datamosh)
    bpy.utils.unregister_class(DATAMOSH_OT_get_start_frames)
