import bpy


class SYNCTHEMLIPS_PT_panel(bpy.types.Panel):
    bl_label = "Sync Them Lips"
    bl_idname = "SYNCTHEMLIPS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Sync Them Lips"
    bl_context = "posemode"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        s = context.scene.sync_them_lips

        bone = context.active_pose_bone
        layout.label(text=f"Bone: {bone.name}" if bone else "Select a mouth bone", icon='BONE_DATA')

        col = layout.column(heading="Mouth")
        col.prop(s, "axis")
        col.prop(s, "closed_value")
        col.prop(s, "open_value")

        box = layout.box()
        box.label(text="Audio Analysis")
        box.prop(s, "threshold")
        box.prop(s, "normalize")
        box.prop(s, "attack")
        box.prop(s, "release")
        box.prop(s, "low_hz")
        box.prop(s, "high_hz")

        box = layout.box()
        box.label(text="Output")
        box.prop(s, "action_prefix")
        box.prop(s, "track_name")
        box.prop(s, "interpolation")
        box.prop(s, "gap_frames")
        box.prop(s, "add_sound_strips")
        box.prop(s, "extend_scene_end")

        layout.operator("sync_them_lips.bake_voicelines", icon='SOUND')
        layout.separator(factor=2.0)
        layout.operator("sync_them_lips.clear_voicelines", icon='TRASH')
