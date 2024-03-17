import bpy 

obj = None
armature = None

# remove empty vertex groups from the object
def removeVertexGroupsWithoutWeights():
    maxWeight = {}
    for i in mesh.vertex_groups:
        maxWeight[i.index] = 0

    for v in mesh.data.vertices:
        for g in v.groups:
            gn = g.group
            try:
                w = obj.vertex_groups[g.group].weight(v.index)
                if (maxWeight.get(gn) is None or w>maxWeight[gn]):
                    maxWeight[gn] = w
            except:
                continue
    # fix bug pointed out by user2859
    ka = []
    ka.extend(maxWeight.keys())
    ka.sort(key=lambda gn: -gn)
    print (ka)
    for gn in ka:
        if maxWeight[gn]<=0:
            print ("delete %d"%gn)
            mesh.vertex_groups.remove(mesh.vertex_groups[gn]) # actually remove the group
      
def remove_invalid_vertex_groups():
    bpy.context.view_layer.objects.active = mesh
    armature = mesh.parent
    
    # Get the set of bone names in the armature
    valid_bone_names = {bone.name for bone in armature.data.bones}
    
    groups_to_delete = []
   
    # Iterate over the vertex groups of the mesh
    for vertex_group in mesh.vertex_groups:
        # Check if the bone exists in the armature
        if vertex_group.name not in valid_bone_names:
            groups_to_delete.append(vertex_group.name)
    
    if len(groups_to_delete) == 0:
        print("All vertices are assigned to valid groups.")
        return        
                        
    # Iterate over the specified vertex groups
    for group_name in groups_to_delete:
        # Check if the vertex group exists
        if group_name in mesh.vertex_groups:
            # Remove the vertex group
            mesh.vertex_groups.remove(mesh.vertex_groups[group_name])        
    
    print(f"Removed vertex groups: {formatArray(groups_to_delete)}")

selected_meshes = []



if bpy.context.selected_objects:
    for mesh_name in [obj.name for obj in bpy.context.selected_objects if obj.type == 'MESH']:
        selected_meshes.append(mesh_name)
    
    for armature in [obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE']:
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.parent == armature:
                selected_meshes.append(obj.name)
    
for mesh_name in selected_meshes:
    mesh = bpy.data.objects[mesh_name]
    removeVertexGroupsWithoutWeights()
    remove_invalid_vertex_groups()
