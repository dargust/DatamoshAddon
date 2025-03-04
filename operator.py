import bpy
import os
import subprocess
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
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

        start_frames = []
        for sequence in sequence_editor.sequences_all:
            if sequence.type == 'MOVIE':
                frame = sequence.frame_final_start
                if frame > 11:
                    start_frames.append(int(sequence.frame_final_start) - 1)

        if not start_frames:
            self.report({'ERROR'}, "No movie clips found in the VSE timeline.")
            return {'CANCELLED'}
        start_points = []
        end_points = []
        for frame in start_frames:
            start_points.append(frame - 10)
            end_points.append(frame + 60)


        print(f"Movie clip start frames: {start_frames}")

        convert_to_avi(input_file, temp_file)
        avi_data = extract_avi_data(temp_file)
        create_datamoshed_avi(avi_data, temp_file, output_file, start_at=start_points, end_at=end_points, duplicated_p_frames=0, transition_frames=start_frames)
        self.report({'INFO'}, "Datamoshing complete")

        # Add the output_file as a new movie sequence to the timeline
        bpy.ops.sequencer.movie_strip_add(filepath=output_file, frame_start=1)
        # Turn off proxy for the newly added movie strip
        new_strip = sequence_editor.sequences_all[-1]
        new_strip.use_proxy = False
        return {'FINISHED'}