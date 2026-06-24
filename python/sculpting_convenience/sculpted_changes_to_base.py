import bpy

# you have sculpted a mesh and now want to re-shape the original with all the shapekeys? Don't worry, here you go!
# This _requires_ the vertices to be identical! You can sculpt all you like, but you can't change the vertex count or -order!
 
# FIRST, import all morphtargets, then DUPLICATE the base head mesh, and name the duplicate "sculptme"
# SECOND, apply surface deforms - every mesh must be bound to sculptme (https://github.com/manavortex/cyberpunk2077/blob/master/python/sculpting_convenience/surface_deform/add_surface_deform.py)
# THIRD, import your already-sculpted head mesh
# 
# In the OUTLINER (top right), SELECT (click on) your "sculptme" mesh
# Then, hold CTRL and click on the already-sculpted head
#
# Afterwards, just click play

# Info popup
def showPopup(title, message_):
    try:
        from ctypes import windll
        windll.user32.MessageBoxW(None, message_, title, 1)
    except:
        # Fallback no-op or Blender custom message fallback
        print(f"{title}: {message_}")

def select_basis_shapekey(mesh):
    shape_key_name = "Basis"
    if not mesh.data.shape_keys.key_blocks:
        mesh.shape_key_add(name=shape_key_name)
        return
    shape_key = mesh.data.shape_keys.key_blocks[shape_key_name]
    mesh.active_shape_key_index = list(mesh.data.shape_keys.key_blocks).index(shape_key)
 
"""Return the vertex data of the Basis shapekey, or fallback to mesh vertices."""
def get_basis_vertices(mesh):
    select_basis_shapekey(mesh)
    if mesh.type != 'MESH':
        return None
    if mesh.data.shape_keys and "Basis" in mesh.data.shape_keys.key_blocks:
        return mesh.data.shape_keys.key_blocks["Basis"].data
    return mesh.data.vertices


def get_vertex_offsets(mesh_without_sculpts, mesh_with_sculpts):
    
    basis_orig = get_basis_vertices(mesh_without_sculpts)
    basis_sculpt = get_basis_vertices(mesh_with_sculpts)
    
    # Ensure both meshes have the same number of vertices
    if len(basis_orig) != len(basis_sculpt):
        showPopup("Vertex count error", "The vertex counts of the original and re-sculpted meshes don't match.")
        return None

    offsets = []
    for i in range(len(basis_orig)):
        offset = basis_sculpt[i].co - basis_orig[i].co
        offsets.append(offset)
        
    return offsets

def apply_vertex_offsets_to_mesh(mesh, offsets):
    # Ensure we're in object mode
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    
    shape_key_name = "Deform"        

    try:
        shape_key = mesh.data.shape_keys.key_blocks[shape_key_name]
        mesh.shape_key_remove(shape_key)
    except:
        print("No shape key to delete :)")        

    shape_key = mesh.shape_key_add(name=shape_key_name)
    shape_key.value = 1.0

    # Apply the offsets to the mesh's shape key
    for i, vert in enumerate(mesh.data.vertices):
        if i >= len(offsets):
            break    
        shape_key.data[i].co += offsets[i]
            
def has_surface_deform_bound_to(target_obj):
    if target_obj is None:
        return False

    for obj in (x for x in bpy.data.objects if x.type == "MESH"):
        for mod in obj.modifiers:
            if mod.type == 'SURFACE_DEFORM' and mod.target == target_obj:
                return True
    return False


def main():
    
    if len(bpy.context.selected_objects) != 2:
        showPopup("Invalid selection", "Please select first the original head, and then your sculpted head")
        return
    
    active_mesh = bpy.context.view_layer.objects.active
    selected_mesh = next(x for x in bpy.context.selected_objects if x.type == "MESH" and x != active_mesh)
    
    if active_mesh is None or selected_mesh is None:
        showPopup("Invalid selection", "Selection mesh names not found")            
            
    mesh_without_sculpts = bpy.data.objects.get(active_mesh.name)
    mesh_with_sculpts = bpy.data.objects.get(selected_mesh.name)  # the mesh that already has the correct shape
    
    if mesh_without_sculpts is None or mesh_with_sculpts is None:    
        showPopup("Invalid selection", "Failed to retrieve meshes from your selection")
        return
   
    # check if the resculpt_mesh has a surface_deform
    if any(m.type == "SURFACE_DEFORM" for m in mesh_with_sculpts.modifiers):
        showPopup("Invalid modifier", f"Please delete the surface deform modifier from {mesh_with_sculpts.name}")
        return
    
    offsets = get_vertex_offsets(mesh_without_sculpts, mesh_with_sculpts)
    if offsets is None:
        showPopup("No offsets found", "Failed to find mesh offsets")
        return
    
    if not has_surface_deform_bound_to(mesh_without_sculpts):
        showPopup("Surface Deform missing", "Your target mesh doesn't seem to have any surface deform modifiers bound to it. Apply them via script first, or click 'OK' to proceed anyway.")

    apply_vertex_offsets_to_mesh(mesh_without_sculpts, offsets)

if __name__ == "__main__":
    main()
