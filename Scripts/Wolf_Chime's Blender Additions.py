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


# =============================================================================
# Keybinds (single source of truth)
# All binds are Ctrl+Alt+Shift + <KEY> by design.
# =============================================================================

MODS = dict(ctrl=True, alt=True, shift=True)

# Each entry:
#   label: human-friendly note
#   keymap_name: Blender keymap name (e.g., "3D View", "Mesh")
#   space_type: keymap space (e.g., "VIEW_3D", "EMPTY")
#   idname: operator bl_idname
#   type: Blender key identifier ("Q", "W", "ONE", etc.)
#   value: usually "PRESS"
KEYBINDS = [
    dict(
        label="Cycle Pivot",
        keymap_name="3D View",
        space_type="VIEW_3D",
        idname="view3d.cycle_pivot",
        type="Q",
        value="PRESS",
        **MODS,
    ),
    dict(
        label="Cycle Transform Orientation",
        keymap_name="3D View",
        space_type="VIEW_3D",
        idname="view3d.cycle_transform_orientation",
        type="W",
        value="PRESS",
        **MODS,
    ),
    dict(
        label="Smooth Vertices (Edit Mode)",
        keymap_name="Mesh",
        space_type="EMPTY",
        idname="view3d.smooth_vertices",
        type="ONE",
        value="PRESS",
        **MODS,
    ),
]


# -------------------------
# Helpers
# -------------------------

def _cycle_value(current, options):
    """Return the next value in options after current (wraps around)."""
    try:
        idx = options.index(current)
    except ValueError:
        idx = -1
    return options[(idx + 1) % len(options)]


addon_keymaps = []  # list[(km, kmi)]


def _remove_addon_kmis_by_idname(km, idnames):
    """Remove any existing addon keymap items in km that match our operator idnames."""
    for kmi in list(km.keymap_items):
        if kmi.idname in idnames:
            km.keymap_items.remove(kmi)


def _warn_on_collisions(binds):
    seen = set()
    for b in binds:
        sig = (
            b["keymap_name"],
            b.get("space_type", ""),
            b["type"],
            b.get("value", "PRESS"),
            bool(b.get("ctrl")),
            bool(b.get("alt")),
            bool(b.get("shift")),
            bool(b.get("oskey")),
        )
        if sig in seen:
            print(f"[Wolf_Chime] WARNING: duplicate binding signature: {sig} ({b.get('label','')})")
        else:
            seen.add(sig)


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    _warn_on_collisions(KEYBINDS)

    # Group binds by keymap so we only create each keymap once.
    by_km = {}
    for b in KEYBINDS:
        key = (b["keymap_name"], b.get("space_type", "EMPTY"))
        by_km.setdefault(key, []).append(b)

    for (km_name, space_type), binds in by_km.items():
        km = kc.keymaps.new(name=km_name, space_type=space_type)

        # Remove old KMIs for OUR operators in this keymap, so reloading the addon doesn't duplicate.
        idnames = {b["idname"] for b in binds}
        _remove_addon_kmis_by_idname(km, idnames)

        # Add KMIs from the table.
        for b in binds:
            kmi = km.keymap_items.new(
                b["idname"],
                type=b["type"],
                value=b.get("value", "PRESS"),
                ctrl=b.get("ctrl", False),
                alt=b.get("alt", False),
                shift=b.get("shift", False),
                oskey=b.get("oskey", False),
            )
            addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()


# -------------------------
# Operators
# -------------------------

class VIEW3D_OT_cycle_pivot(bpy.types.Operator):
    bl_idname = "view3d.cycle_pivot"
    bl_label = "Cycle Transform Pivot"
    bl_options = {'REGISTER'}

    pivots = (
        'MEDIAN_POINT',
        'CURSOR',
        'INDIVIDUAL_ORIGINS',
        'ACTIVE_ELEMENT',
        'BOUNDING_BOX_CENTER',
    )

    def execute(self, context):
        ts = context.scene.tool_settings
        ts.transform_pivot_point = _cycle_value(ts.transform_pivot_point, self.pivots)
        return {'FINISHED'}


class VIEW3D_OT_smooth_vertices(bpy.types.Operator):
    bl_idname = "view3d.smooth_vertices"
    bl_label = "Smooth Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        bpy.ops.mesh.vertices_smooth()
        return {'FINISHED'}


class VIEW3D_OT_cycle_orientation(bpy.types.Operator):
    bl_idname = "view3d.cycle_transform_orientation"
    bl_label = "Cycle Transform Orientation"
    bl_options = {'REGISTER'}

    orientations = (
        'GLOBAL',
        'LOCAL',
        'VIEW',
        'CURSOR',
    )

    def execute(self, context):
        slot = context.scene.transform_orientation_slots[0]
        slot.type = _cycle_value(slot.type, self.orientations)
        return {'FINISHED'}


# -------------------------
# Registration
# -------------------------

_CLASSES = (
    VIEW3D_OT_cycle_pivot,
    VIEW3D_OT_cycle_orientation,
    VIEW3D_OT_smooth_vertices,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
