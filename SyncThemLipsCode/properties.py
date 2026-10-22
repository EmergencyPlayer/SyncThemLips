import bpy
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       IntProperty, StringProperty)


class SyncThemLipsSettings(bpy.types.PropertyGroup):
    action_prefix: StringProperty(
        name="Action Name",
        default="Mouth ControlAction",
        description="Base name for each generated action and NLA strip. A number is appended (e.g. 'EP Mouth ControlAction 3')",
    )
    track_name: StringProperty(
        name="NLA Track",
        default="Sync Them Lips",
        description="NLA track the strips are placed on. Created if it doesn't exist; new strips are added after the last one",
    )
    axis: EnumProperty(
        name="Axis",
        items=[
            ('0', "X", "Move the mouth bone along its local X axis"),
            ('1', "Y", "Move the mouth bone along its local Y axis"),
            ('2', "Z", "Move the mouth bone along its local Z axis"),
        ],
        default='1',
        description="Location axis of the bone that opens and closes the mouth",
    )
    closed_value: FloatProperty(
        name="Closed", default=0.01, precision=3,
        description="Bone location value when the mouth is closed",
    )
    open_value: FloatProperty(
        name="Open", default=0.11, precision=3,
        description="Bone location value when the mouth is open",
    )
    threshold: FloatProperty(
        name="Threshold", default=0.05, min=0.0, max=1.0,
        description="Minimum loudness for the mouth to open. Relative to the loudest point in each clip (0-1) when Normalize is on",
    )
    normalize: BoolProperty(
        name="Normalize", default=True,
        description="Scale each clip so its peak is 1.0, so one threshold fits every voiceline",
    )
    attack: FloatProperty(
        name="Attack", default=0.0, min=0.0, unit='TIME_ABSOLUTE',
        description="How quickly the loudness reading rises. Higher values smooth out sudden spikes and reduce flicker",
    )
    release: FloatProperty(
        name="Release", default=0.0, min=0.0, unit='TIME_ABSOLUTE',
        description="How slowly the loudness reading falls. Higher values keep the mouth reacting through short dips",
    )
    low_hz: FloatProperty(
        name="Low Cut (Hz)", default=0.0, min=0.0,
        description="Ignore sound below this frequency (e.g. rumble). 0 = off",
    )
    high_hz: FloatProperty(
        name="High Cut (Hz)", default=0.0, min=0.0,
        description="Ignore sound above this frequency (e.g. hiss). 0 = off",
    )
    interpolation: EnumProperty(
        name="Interpolation",
        items=[
            ('BEZIER', "Bezier", "Smooth transitions between open and closed"),
            ('LINEAR', "Linear", "Straight-line transitions between open and closed"),
            ('CONSTANT', "Constant", "Instant snap between open and closed"),
        ],
        default='BEZIER',
        description="How the mouth moves between keyframes",
    )
    gap_frames: IntProperty(
        name="Gap (frames)", default=0, min=0,
        description="Empty frames left between one voiceline strip and the next",
    )
    add_sound_strips: BoolProperty(
        name="Add Audio to Sequencer", default=True,
        description="Also place each audio file in the Video Sequencer at the same position, so you can hear it while scrubbing",
    )
    extend_scene_end: BoolProperty(
        name="Extend Scene End", default=True,
        description="Move the scene's end frame out to the last strip if it falls past the current end",
    )