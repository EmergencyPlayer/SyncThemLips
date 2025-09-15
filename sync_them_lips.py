import bpy

# Customize these to match your scene:
armature_obj_name = "MouthRig"        # ← your Armature *object* in the Outliner
bone_name         = "Mouth_Controller" # your bone
action_name       = "Mouth_Smile"      # Action with your baked X-loc curve

scene = bpy.context.scene
start_frame = scene.frame_start
end_frame   = scene.frame_end

# Grab your armature object and the Action
arm = bpy.data.objects[armature_obj_name]
act = bpy.data.actions[action_name]


# Grab the Y-location F-curve (array_index = 1)
y_curve = next(
    fc for fc in act.fcurves
    if fc.data_path == f'pose.bones["{bone_name}"].location'
       and fc.array_index == 1
)

print(f"Found Y-loc F-Curve with {len(y_curve.keyframe_points)} keys.")

# First pass: sample slope and store target Y for each frame
frame_targets = []
for frame in range(start_frame, end_frame + 1):
    cur  = y_curve.evaluate(frame)
    prev = y_curve.evaluate(frame - 1)
    y_val = 0.134 if (cur - prev) > 0 else 0.074
    frame_targets.append((frame, y_val))

# Second pass: apply & keyframe
for frame, y_val in frame_targets:
    scene.frame_set(frame)
    pb = arm.pose.bones[bone_name]
    pb.location.y = y_val
    pb.keyframe_insert(data_path="location", index=1)

print("Done baking slope-based Y-loc keys (two-pass).")
