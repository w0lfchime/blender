bl_info = {
    "name": "Wolf_Chime's Blender Additions",
    "author": "wolf",
    "version": (1, 1, 0),
    "blender": (5, 0, 1),
    "location": "3D View",
    "description": "Adds various hotkeys",
    "category": "3D View",
}

import bpy


class VIEW3D_OT_cycle_pivot(bpy.types.Operator):
    bl_idname = "view3d.cycle_pivot"
    bl_label = "Cycle Transform Pivot"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pivots = (
            'MEDIAN_POINT',
            'CURSOR',
            'INDIVIDUAL_ORIGINS',
            'ACTIVE_ELEMENT',
            'BOUNDING_BOX_CENTER',
        )

        ts = context.scene.tool_settings
        cur = ts.transform_pivot_point

        try:
            i = pivots.index(cur)
        except ValueError:
            i = 0

        ts.transform_pivot_point = pivots[(i + 1) % len(pivots)]
        return {'FINISHED'}


class VIEW3D_OT_cycle_orientation(bpy.types.Operator):
    bl_idname = "view3d.cycle_transform_orientation"
    bl_label = "Cycle Transform Orientation"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Common built-in orientations. (You can add/remove if you want.)
        orientations = (
            'GLOBAL',
            'LOCAL',
            #'NORMAL',
            #'GIMBAL',
            'VIEW',
            'CURSOR',
            #'PARENT',
        )

        scene = context.scene

        # Primary (active) orientation slot is index 0.
        # This matches the UI's orientation dropdown.
        slot = scene.transform_orientation_slots[0]
        cur = slot.type

        try:
            i = orientations.index(cur)
        except ValueError:
            i = 0

        slot.type = orientations[(i + 1) % len(orientations)]
        return {'FINISHED'}


addon_keymaps = []


def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    # Remove old addon-created bindings for these operators (prevents duplicates)
    op_ids = {
        VIEW3D_OT_cycle_pivot.bl_idname,
        VIEW3D_OT_cycle_orientation.bl_idname,
    }
    for kmi in list(km.keymap_items):
        if kmi.idname in op_ids:
            km.keymap_items.remove(kmi)

    # Ctrl+Alt+Shift+Q -> cycle pivot
    kmi_pivot = km.keymap_items.new(
        VIEW3D_OT_cycle_pivot.bl_idname,
        type="Q",
        value="PRESS",
        ctrl=True,
        alt=True,
        shift=True
    )
    addon_keymaps.append((km, kmi_pivot))

    # Ctrl+Alt+Shift+W -> cycle transform orientation
    kmi_orient = km.keymap_items.new(
        VIEW3D_OT_cycle_orientation.bl_idname,
        type="W",
        value="PRESS",
        ctrl=True,
        alt=True,
        shift=True
    )
    addon_keymaps.append((km, kmi_orient))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()




class VIEW3D_OT_smooth_vertices(bpy.types.Operator):
    bl_idname = "view3d.smooth_vertices"
    bl_label = "Smooth Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)
        return {'FINISHED'}





def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    # Remove old bindings for smooth to prevent dupes
    for kmi in list(km.keymap_items):
        if kmi.idname == VIEW3D_OT_smooth_vertices.bl_idname:
            km.keymap_items.remove(kmi)

    # Bind Ctrl+Shift+1
    kmi = km.keymap_items.new(
        VIEW3D_OT_smooth_vertices.bl_idname,
        type='ONE',
        value='PRESS',
        ctrl=True,
        shift=True
    )

    addon_keymaps.append((km, kmi))

def register():
    bpy.utils.register_class(VIEW3D_OT_cycle_pivot)
    bpy.utils.register_class(VIEW3D_OT_cycle_orientation)
    bpy.utils.register_class(VIEW3D_OT_smooth_vertices) 
    register_keymap()


def unregister():
    unregister_keymap()
    bpy.utils.unregister_class(VIEW3D_OT_cycle_orientation)
    bpy.utils.unregister_class(VIEW3D_OT_cycle_pivot)
    bpy.utils.unregister_class(VIEW3D_OT_smooth_vertices) 
