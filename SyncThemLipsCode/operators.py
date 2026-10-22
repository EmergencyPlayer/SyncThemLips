import os
import re

import bpy
from bpy.props import CollectionProperty, StringProperty

from . import audio, lipsync


def _natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


class SYNCTHEMLIPS_OT_bake(bpy.types.Operator):
    bl_idname = "sync_them_lips.bake_voicelines"
    bl_label = "Sync Them Lips"
    bl_description = "Bake each selected audio file into a mouth action and stack them on the NLA"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(subtype='DIR_PATH')
    files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'SKIP_SAVE'})
    filter_glob: StringProperty(default="*.wav;*.mp3;*.flac;*.ogg;*.m4a;*.aac;*.aiff", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'ARMATURE' and ob.mode == 'POSE'
                and context.active_pose_bone is not None)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        s = context.scene.sync_them_lips
        scene = context.scene
        arm = context.active_object
        bone = context.active_pose_bone
        fps = scene.render.fps / scene.render.fps_base

        names = sorted((f.name for f in self.files), key=_natural_key)
        if not names:
            self.report({'ERROR'}, "No audio files selected")
            return {'CANCELLED'}

        anim = arm.animation_data_create()
        track = lipsync.get_track(anim, s.track_name)
        done, failed = 0, []

        wm = context.window_manager
        wm.progress_begin(0, len(names))
        for i, fname in enumerate(names):
            path = os.path.join(self.directory, fname)
            try:
                env = audio.load_envelope(path, fps, s.low_hz, s.high_hz,
                                          s.attack, s.release, s.normalize)
                targets = audio.slope_targets(env, s.closed_value, s.open_value, s.threshold)

                index = len(track.strips) + 1
                name = f"{s.action_prefix} {index}"
                action, slot = lipsync.build_action(arm, bone.name, int(s.axis),
                                                    name, targets, s.interpolation)
                start = lipsync.next_start(track, scene.frame_start, s.gap_frames)
                strip = lipsync.push_to_track(track, action, slot, name, start)

                if s.add_sound_strips:
                    lipsync.add_sound_strip(scene, path, os.path.splitext(fname)[0], start)
                if s.extend_scene_end and strip.frame_end > scene.frame_end:
                    scene.frame_end = int(strip.frame_end)
                done += 1
            except Exception as e:  # keep going; report at the end
                failed.append(f"{fname}: {e}")
            wm.progress_update(i + 1)
        wm.progress_end()

        for msg in failed:
            self.report({'WARNING'}, msg)
        self.report({'INFO'}, f"Baked {done}/{len(names)} voicelines onto '{track.name}'")
        return {'FINISHED'} if done else {'CANCELLED'}


class SYNCTHEMLIPS_OT_clear(bpy.types.Operator):
    bl_idname = "sync_them_lips.clear_voicelines"
    bl_label = "Clear Voicelines"
    bl_description = "Delete every generated strip, action and audio strip so you can redo the voicelines"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def _our_tracks(context):
        ob = context.active_object
        if not (ob and ob.type == 'ARMATURE' and ob.animation_data):
            return []
        name = context.scene.sync_them_lips.track_name
        return [
            t for t in ob.animation_data.nla_tracks
            if t.name == name
            or any(st.action and st.action.get("sync_them_lips") for st in t.strips)
        ]

    @classmethod
    def poll(cls, context):
        if not cls._our_tracks(context):
            cls.poll_message_set("No Sync Them Lips track found on the active armature")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event,
            title="Clear all voicelines?",
            message="This deletes every strip and action on the track. Ctrl+Z can undo it.",
            confirm_text="Delete",
            icon='WARNING',
        )

    def execute(self, context):
        scene = context.scene
        anim = context.active_object.animation_data
        tracks = self._our_tracks(context)

        actions = {st.action for t in tracks for st in t.strips if st.action}
        for track in tracks:
            for st in list(track.strips):
                track.strips.remove(st)
            anim.nla_tracks.remove(track)

        removed_actions = 0
        for act in actions:
            if act.users == 0:
                bpy.data.actions.remove(act)
                removed_actions += 1

        removed_audio = 0
        seq = scene.sequence_editor
        if seq:
            coll = seq.strips if hasattr(seq, "strips") else seq.sequences
            for st in [s for s in coll if s.get("sync_them_lips")]:
                coll.remove(st)
                removed_audio += 1

        self.report({'INFO'}, f"Cleared {removed_actions} actions and {removed_audio} audio strips")
        return {'FINISHED'}