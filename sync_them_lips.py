import bpy

# 1) Customize these to match your scene:
armature_obj_name = "EP Mouth Control"         # your Armature object name in Outliner
bone_name         = "EPMouthControl" # your bone
action_name       = "EP Mouth ControlAction"      # Action with your baked X-loc curve

# Mouth Parameters
closed_mouth = 0.01
open_mouth = 0.11
vo_threshold = 0.01

scene = bpy.context.scene
start_frame = scene.frame_start
end_frame   = scene.frame_end

arm = bpy.data.objects[armature_obj_name]

# 2) Grab your Action
act = bpy.data.actions[action_name]

# 3) Get the channelbag corresponding to the armature object
#    This handles the new “slots / strips / channelbag” structure.
from bpy_extras.anim_utils import action_ensure_channelbag_for_slot

# Ensure there is a slot suitable for the armature and get the channelbag:
slot = act.slots[0]  # typically the first (or only) slot; adjust if multiple
chanbag = action_ensure_channelbag_for_slot(act, slot)

# 4) Grab the Y-location F-curve (array_index = 1)
fcurves = chanbag.fcurves
y_curve = next(
    fc for fc in fcurves
    if fc.data_path == f'pose.bones["{bone_name}"].location'
       and fc.array_index == 1
)

print(f"Found Y-loc F-Curve with {len(y_curve.keyframe_points)} keys.")

# 5) First pass: sample slope and store target Y for each frame
frame_targets = []
for frame in range(start_frame, end_frame + 1):
    cur  = y_curve.evaluate(frame)
    prev = y_curve.evaluate(frame - 1)
    y_val = closed_mouth
    if (cur - prev) > 0 and cur > vo_threshold: 
        y_val = open_mouth
    frame_targets.append((frame, y_val))

# 6) Second pass: apply & keyframe
for frame, y_val in frame_targets:
    scene.frame_set(frame)
    pb = arm.pose.bones[bone_name]
    pb.location.y = y_val
    pb.keyframe_insert(data_path="location", index=1)

print("Done baking slope-based Y-loc keys (two-pass).")
