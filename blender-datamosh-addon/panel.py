import bpy

class DATAMOSH_PT_panel(bpy.types.Panel):
    bl_label = "Datamosh"
    bl_idname = "DATAMOSH_PT_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Datamosh'

    def draw(self, context):
        layout = self.layout
        layout.operator("datamosh.run_datamosh")