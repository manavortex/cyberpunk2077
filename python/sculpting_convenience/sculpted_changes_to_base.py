import bpy

# you have sculpted a mesh and now want to re-shape the original with all the shapekeys? Don't worry, here you go!
# This _requires_ the vertices to be identical! You can sculpt all you like, but you can't change the vertex count or -order!

original_mesh_name = 'OriginalMesh'
resculpted_mesh_name = 'ResculptMesh'

apply_deforms_to_visible_objects = True

def get_vertex_offsets(original_mesh, resculpt_mesh):
    offsets = []

    # Ensure both meshes have the same number of vertices
    if len(original_mesh.data.vertices) != len(resculpt_mesh.data.vertices):
        print("The vertex counts of the original and re-sculpted meshes don't match.")
        return None

    # Calculate the offsets
    for i, v_orig in enumerate(original_mesh.data.vertices):
        v_resculpt = resculpt_mesh.data.vertices[i]
        offset = v_resculpt.co - v_orig.co
        offsets.append(offset)

    return offsets

def apply_vertex_offsets_to_mesh(mesh, offsets):
    # Ensure we're in object mode
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    # Duplicate the mesh to preserve the original
    deformed_mesh = mesh.copy()
    deformed_mesh.data = mesh.data.copy()
    bpy.context.collection.objects.link(deformed_mesh)

    # Create a new shapekey if the mesh doesn't have any
    if not deformed_mesh.data.shape_keys:
        deformed_mesh.shape_key_add(name="Basis")

    shape_key = deformed_mesh.shape_key_add(name="Deform")

    # Apply the offsets to the mesh's shape key
    for i, vert in enumerate(deformed_mesh.data.vertices):
        if i < len(offsets):
            shape_key.data[i].co += offsets[i]

    return deformed_mesh

# Apply the offsets to all visible meshes
def apply_to_visible_meshes(offsets, original_mesh, resculpt_mesh):
    if apply_deforms_to_visible_objects != True:
        return

    for mesh in bpy.context.view_layer.objects:
        if mesh.type == 'MESH' and mesh.name not in [original_mesh.name, resculpt_mesh.name] and mesh.visible_get():
            deformed_mesh = apply_vertex_offsets_to_mesh(mesh, offsets)
            print(f"Applied offsets to {deformed_mesh.name}")

def main():
    original_mesh = bpy.data.objects.get(original_mesh_name)  # Replace with your original mesh name
    resculpt_mesh = bpy.data.objects.get(resculpted_mesh_name)  # Replace with your re-sculpted mesh name

    if original_mesh is None or resculpt_mesh is None:
        print("Original or resculpted mesh not found!")
        return

    offsets = get_vertex_offsets(original_mesh, resculpt_mesh)
    if offsets is None:
        return

    apply_to_visible_meshes(offsets, original_mesh, resculpt_mesh)

if __name__ == "__main__":
    main()
