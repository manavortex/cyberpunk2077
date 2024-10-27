import bpy

def delete_all_shapekeys(obj):
    """Deletes all shapekeys for a given object, iterating backwards."""
    if obj.data.shape_keys:
        for key_block in reversed(obj.data.shape_keys.key_blocks):
            obj.shape_key_remove(key_block)


def replace_mesh_with_copy(mesh, mesh_copy):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh.data = mesh_copy.data.copy()
    bpy.data.objects.remove(mesh_copy, do_unlink=True)

    print(f"Replaced vertex data for mesh '{mesh.name}'")


def apply_shrinkwrap_to_shapekeys(mesh, modifier_name="Shrinkwrap"):
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    shrinkwrap_mod = mesh.modifiers.get(modifier_name)
    if shrinkwrap_mod is None:
        print(f"No Shrinkwrap modifier found on {mesh.name}.")
        return

    mesh_copy = mesh.copy()
    mesh_copy.data = mesh.data.copy()
    bpy.context.collection.objects.link(mesh_copy)
    
    bpy.context.view_layer.objects.active = mesh_copy
    delete_all_shapekeys(mesh_copy)
    bpy.ops.object.modifier_apply(modifier=modifier_name) 
    
    if mesh.data.shape_keys is not None:      
        deformed_verts = [v.co for v in mesh_copy.data.vertices]   
        shape_keys = mesh.data.shape_keys.key_blocks
        for shapekey in shape_keys:
            mesh.active_shape_key_index = list(shape_keys.keys()).index(shapekey.name)
            
            for i, vert in enumerate(mesh.data.vertices):
                shapekey.data[i].co += deformed_verts[i] - vert.co
            
            print(f"Applied Shrinkwrap offsets to shapekey '{shapekey.name}' for mesh '{mesh.name}'")            
        bpy.data.objects.remove(mesh_copy)
    else:
        replace_mesh_with_copy(mesh, mesh_copy)


def apply_shrinkwrap_to_all_objects():
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and any(mod.type == 'SHRINKWRAP' for mod in obj.modifiers):
            print(f"Applying Shrinkwrap to '{obj.name}'...")
            apply_shrinkwrap_to_shapekeys(obj, "Shrinkwrap")
        else:
            print(f"Skipping '{obj.name}': No Shrinkwrap modifier found.")


if __name__ == "__main__":
    apply_shrinkwrap_to_all_objects()
