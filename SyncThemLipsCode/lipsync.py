import math

import bpy


def build_action(arm, bone_name, axis, name, targets, interpolation):
    """Create a slotted Action containing one location F-curve, keys at 0..N."""
    action = bpy.data.actions.new(name)
    slot = action.slots.new('OBJECT', arm.name)
    layer = action.layers.new("Layer")
    strip = layer.strips.new(type='KEYFRAME')
    channelbag = strip.channelbag(slot, ensure=True)

    path = f'pose.bones["{bpy.utils.escape_identifier(bone_name)}"].location'
    fc = channelbag.fcurves.new(path, index=axis)
    for frame, value in enumerate(targets):
        fc.keyframe_points.insert(frame, value, options={'FAST'})
    for kp in fc.keyframe_points:
        kp.interpolation = interpolation
    fc.update()
    return action, slot


def get_track(anim_data, track_name):
    for track in anim_data.nla_tracks:
        if track.name == track_name:
            return track
    track = anim_data.nla_tracks.new()
    track.name = track_name
    return track


def next_start(track, default_start, gap):
    if len(track.strips):
        return math.ceil(max(s.frame_end for s in track.strips)) + gap
    return default_start


def push_to_track(track, action, slot, name, start):
    strip = track.strips.new(name, int(start), action)
    strip.extrapolation = 'NOTHING'   # "Hold" -> "Nothing"
    try:
        strip.action_slot = slot
    except (AttributeError, TypeError):
        pass
    return strip


def add_sound_strip(scene, filepath, name, start):
    seq = scene.sequence_editor_create()
    coll = seq.strips if hasattr(seq, "strips") else seq.sequences
    return coll.new_sound(name, filepath, 1, int(start))
