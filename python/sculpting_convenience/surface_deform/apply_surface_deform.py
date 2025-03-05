import bpy

def delete_all_shapekeys(obj):
    """Deletes all shapekeys for a given object, iterating backwards."""
    if obj.data.shape_keys:
        for key_block in reversed(obj.data.shape_keys.key_blocks):
            obj.shape_key_remove(key_block)

def replace_mesh_with_copy(mesh, mesh_copy):
    """Replaces the vertex data of the original mesh with the copied mesh."""
    # Delete all vertices from the original mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Replace the original mesh data with the copied mesh data
    mesh.data = mesh_copy.data.copy()

    # Remove the temporary mesh copy
    bpy.data.objects.remove(mesh_copy, do_unlink=True)
    print(f"Replaced vertex data for mesh '{mesh.name}'")

def apply_surface_deform_to_shapekeys(mesh, modifier_name="Surface Deform"):
    """Applies Surface Deform modifier to shapekeys or replaces mesh data if no shapekeys exist."""
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    # Check if the Surface Deform modifier exists
    surf_def_mod = mesh.modifiers.get(modifier_name)
    if not surf_def_mod:
        print(f"No Surface Deform modifier found on {mesh.name}.")
        return

    # Create a temporary copy of the mesh to apply the modifier
    mesh_copy = mesh.copy()
    mesh_copy.data = mesh.data.copy()
    bpy.context.collection.objects.link(mesh_copy)

    # Apply the Surface Deform modifier to the copy
    bpy.context.view_layer.objects.active = mesh_copy
    delete_all_shapekeys(mesh_copy)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
    except Exception as e:
        print(f"Failed applying Surface Deform to mesh '{mesh.name}': {e}")
        bpy.data.objects.remove(mesh_copy, do_unlink=True)
        return

    if mesh.data.shape_keys:
        # Apply the deformed vertex positions to each shapekey
        deformed_verts = [v.co for v in mesh_copy.data.vertices]
        shape_keys = mesh.data.shape_keys.key_blocks
        for shapekey in shape_keys:
            mesh.active_shape_key_index = shape_keys.keys().index(shapekey.name)
            for i, vert in enumerate(mesh.data.vertices):
                shapekey.data[i].co += deformed_verts[i] - vert.co
            print(f"Applied Surface Deform offsets to shapekey '{shapekey.name}' for mesh '{mesh.name}'")        
        bpy.data.objects.remove(mesh_copy, do_unlink=True)
    else:
        # Replace the original mesh with the modified copy
        replace_mesh_with_copy(mesh, mesh_copy)

def apply_surface_deform_to_all_objects():
    """Applies Surface Deform modifier to all mesh objects in the scene."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and any(mod.type == 'SURFACE_DEFORM' for mod in obj.modifiers):
            print(f"Applying Surface Deform to '{obj.name}'...")
            apply_surface_deform_to_shapekeys(obj)
        else:
            print(f"Skipping '{obj.name}': No Surface Deform modifier found.")

if __name__ == "__main__":
    apply_surface_deform_to_all_objects()
