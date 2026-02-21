bl_info = {
    "name": "Simple PBR Exporter",
    "author": "NDLegion",
    "version": (1, 5, 2),
    "blender": (4, 0, 0),
    "location": "Render Properties",
    "description": "Bake and export PBR textures (BaseColor, Normal, Roughness, Metallic) for Roblox",
    "category": "Render",
}

import bpy
from pathlib import Path

# --------------------------------------------------
# UTILS
# --------------------------------------------------

def safe_name(name: str) -> str:
    forbidden = '<>:"/\\|?*'
    for ch in forbidden:
        name = name.replace(ch, '_')
    return name.strip()


def ensure_cycles(operator=None):
    scene = bpy.context.scene
    if scene.render.engine != 'CYCLES':
        scene.render.engine = 'CYCLES'
        if operator:
            operator.report(
                {'INFO'},
                "Render engine switched to Cycles (required for baking)"
            )


def active_mesh_object():
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return None
    return obj


def prepare_image(name, size, folder, alpha=False):
    img = bpy.data.images.new(
        name=name,
        width=size,
        height=size,
        alpha=alpha
    )
    img.filepath_raw = str(folder / f"{name}.png")
    img.file_format = 'PNG'
    return img


def set_active_image_node(obj, image):
    for slot in obj.material_slots:
        mat = slot.material
        if not mat:
            continue
        if not mat.use_nodes:
            mat.use_nodes = True

        nodes = mat.node_tree.nodes
        img_node = nodes.new("ShaderNodeTexImage")
        img_node.image = image
        nodes.active = img_node


def backup_links(obj):
    backup = {}
    for slot in obj.material_slots:
        mat = slot.material
        if not mat or not mat.use_nodes:
            continue
        tree = mat.node_tree
        backup[mat] = [(l.from_socket, l.to_socket) for l in tree.links]
    return backup


def restore_links(backup):
    for mat, links in backup.items():
        tree = mat.node_tree
        tree.links.clear()
        for from_socket, to_socket in links:
            tree.links.new(from_socket, to_socket)


def bake_value_map(obj, input_name, export_path, size, tex_name):
    """
    Bake single-channel map (Roughness or Metallic)
    from Principled BSDF input using Emission.
    """
    backup = backup_links(obj)

    for slot in obj.material_slots:
        mat = slot.material
        if not mat or not mat.use_nodes:
            continue

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        principled = None
        output = None

        for n in nodes:
            if n.type == 'BSDF_PRINCIPLED':
                principled = n
            elif n.type == 'OUTPUT_MATERIAL':
                output = n

        if not principled or not output:
            continue

        emit = nodes.new("ShaderNodeEmission")
        val = principled.inputs[input_name].default_value
        emit.inputs[0].default_value = (val, val, val, 1.0)
        links.new(emit.outputs[0], output.inputs[0])

    img = prepare_image(tex_name, size, export_path)
    set_active_image_node(obj, img)

    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True

    bpy.ops.object.bake(type='EMIT')
    img.save()

    restore_links(backup)


# --------------------------------------------------
# OPERATOR
# --------------------------------------------------

class SIMPLE_PBR_OT_export(bpy.types.Operator):
    bl_idname = "render.simple_pbr_export"
    bl_label = "Export PBR Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ensure_cycles(self)

        obj = active_mesh_object()
        if not obj:
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}

        if not obj.material_slots:
            self.report({'ERROR'}, "Object has no materials")
            return {'CANCELLED'}

        safe_obj_name = safe_name(obj.name)
        export_root = Path(bpy.path.abspath("//export")) / safe_obj_name
        export_root.mkdir(parents=True, exist_ok=True)

        size = context.scene.simple_pbr_resolution

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        # ---------------- BaseColor ----------------
        img = prepare_image(f"{safe_obj_name}_BaseColor", size, export_root, alpha=False)
        set_active_image_node(obj, img)

        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        bpy.ops.object.bake(type='DIFFUSE')
        img.save()

        # ---------------- Normal ----------------
        img = prepare_image(f"{safe_obj_name}_Normal", size, export_root)
        set_active_image_node(obj, img)

        bpy.context.scene.render.bake.use_pass_color = False
        bpy.ops.object.bake(type='NORMAL')
        img.save()

        # ---------------- Roughness ----------------
        bake_value_map(
            obj,
            "Roughness",
            export_root,
            size,
            f"{safe_obj_name}_Roughness"
        )

        # ---------------- Metallic ----------------
        bake_value_map(
            obj,
            "Metallic",
            export_root,
            size,
            f"{safe_obj_name}_Metallic"
        )

        self.report({'INFO'}, f"PBR textures exported to {export_root}")
        return {'FINISHED'}


# --------------------------------------------------
# UI
# --------------------------------------------------

class SIMPLE_PBR_PT_panel(bpy.types.Panel):
    bl_label = "Simple PBR Exporter"
    bl_idname = "RENDER_PT_simple_pbr_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "simple_pbr_resolution")
        layout.operator("render.simple_pbr_export", icon='EXPORT')


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

def register():
    bpy.utils.register_class(SIMPLE_PBR_OT_export)
    bpy.utils.register_class(SIMPLE_PBR_PT_panel)

    bpy.types.Scene.simple_pbr_resolution = bpy.props.IntProperty(
        name="Texture Resolution",
        default=2048,
        min=256,
        max=8192
    )


def unregister():
    bpy.utils.unregister_class(SIMPLE_PBR_OT_export)
    bpy.utils.unregister_class(SIMPLE_PBR_PT_panel)
    del bpy.types.Scene.simple_pbr_resolution


if __name__ == "__main__":
    register()
