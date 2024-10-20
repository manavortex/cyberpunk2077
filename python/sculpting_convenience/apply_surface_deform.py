import bpy

def delete_all_shapekeys(obj):
    """Deletes all shapekeys for a given object, iterating backwards."""
    if obj.data.shape_keys:
        # Iterate over the shapekeys in reverse order
        for key_block in reversed(obj.data.shape_keys.key_blocks):
            obj.shape_key_remove(key_block)

def apply_surface_deform_to_shapekeys(mesh, modifier_name="Surface Deform"):
    # Ensure we're in object mode
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    # Check if the mesh has shapekeys
    if mesh.data.shape_keys is None:
        print(f"{mesh.name} has no shapekeys.")
        return
    
    # Check if the Surface Deform modifier exists
    surf_def_mod = mesh.modifiers.get(modifier_name)
    if surf_def_mod is None:
        print(f"No Surface Deform modifier found on {mesh.name}.")
        return

    # Get the vertex positions after Surface Deform modifier is applied (temporary basis)
    mesh_copy = mesh.copy()
    mesh_copy.data = mesh.data.copy()
    bpy.context.collection.objects.link(mesh_copy)
    
    # Apply all modifiers except Armature and shapekey-related modifiers
    bpy.context.view_layer.objects.active = mesh_copy
    delete_all_shapekeys(mesh_copy)
    bpy.ops.object.modifier_apply(modifier=modifier_name)
    
    deformed_verts = [v.co for v in mesh_copy.data.vertices]
    
    # Now, apply the offsets to each shapekey
    shape_keys = mesh.data.shape_keys.key_blocks
    
    for shapekey in shape_keys:
        # Switch to this shapekey
        mesh.active_shape_key_index = shape_keys.keys().index(shapekey.name)
        
        # Calculate the offset for each vertex and apply it
        for i, vert in enumerate(mesh.data.vertices):
            shapekey.data[i].co += deformed_verts[i] - vert.co
        
        print(f"Applied Surface Deform offsets to shapekey '{shapekey.name}' for mesh '{mesh.name}'")

    # Delete the Surface Deform modifier
    mesh.modifiers.remove(surf_def_mod)

    # Clean up
    bpy.data.objects.remove(mesh_copy)

def apply_surface_deform_to_all_objects():
    # Iterate through all objects in the scene (whether visible or not)
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Check if the object has a Surface Deform modifier
            if any(mod.type == 'SURFACE_DEFORM' for mod in obj.modifiers):
                print(f"Applying Surface Deform to '{obj.name}'...")
                apply_surface_deform_to_shapekeys(obj)
            else:
                print(f"Skipping '{obj.name}': No Surface Deform modifier found.")

if __name__ == "__main__":
    apply_surface_deform_to_all_objects()
