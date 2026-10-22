import bpy

from . import operators, properties, ui

_classes = (
    properties.SyncThemLipsSettings,
    operators.SYNCTHEMLIPS_OT_bake,
    operators.SYNCTHEMLIPS_OT_clear,
    ui.SYNCTHEMLIPS_PT_panel,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sync_them_lips = bpy.props.PointerProperty(type=properties.SyncThemLipsSettings)


def unregister():
    del bpy.types.Scene.sync_them_lips
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
