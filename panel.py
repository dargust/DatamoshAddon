#############################################################################
# Datamosh addon for blender                                                #
# Copyright (C) 2025 Dan Argust                                             #
#                                                                           #
#    This program is free software: you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License as published by   #
#    the Free Software Foundation, either version 3 of the License, or      #
#    (at your option) any later version.                                    #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>. #
#############################################################################

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