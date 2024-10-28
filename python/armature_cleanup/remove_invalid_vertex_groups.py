import bpy

# credit goes to lucky: https://blenderartists.org/t/how-to-delete-useless-vertex-groups-from-deleted-bones/1185075/8
def delete_nodeform_vgroups(mesh):
    arm = None
    arm = mesh.find_armature()
    if arm == None:
        print("No armature modifier found, add one")
        return
    
    bones_list = [b.name for b in arm.data.bones if b.use_deform]
    
    obj = mesh
    
    if len(obj.vertex_groups) == 0:
        print("No vertex groups found")
        return
    
    else:
        for vgroup in obj.vertex_groups:
            if not vgroup.name in bones_list:
                print("Non deformable vertex group found:", vgroup.name)
                obj.vertex_groups.remove(vgroup)


# Iterate through all selected mesh objects
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        delete_nodeform_vgroups(obj)
