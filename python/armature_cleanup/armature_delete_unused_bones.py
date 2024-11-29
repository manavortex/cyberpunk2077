import bpy
import re

def delete_vertex_groups_without_weights(obj):
    try:
        vertex_groups = obj.vertex_groups
        groups = {r : None for r in range(len(vertex_groups))}

        for vert in obj.data.vertices:
            for vg in vert.groups:
                i = vg.group
                if i in groups:
                    del groups[i]

        lis = [k for k in groups]
        lis.sort(reverse=True)
        for i in lis:
            vertex_groups.remove(vertex_groups[i])
    except:
        pass
    
def delete_vertex_groups_without_corresponding_bone(obj, bone_names):
     
    groups_to_delete = [
        group.name for group in obj.vertex_groups
        if group.name not in bone_names
    ]
    
    # Remove the vertex groups
    for group_name in groups_to_delete:
        group = obj.vertex_groups.get(group_name)
        if group:
            obj.vertex_groups.remove(group)
            print(f"Deleted vertex group '{group_name}' from '{obj.name}'")


def get_all_vertex_groups(armature):
    bpy.ops.object.mode_set(mode='EDIT')
    return {vg.name for mesh in (child for child in armature.children if child.type == 'MESH') for vg in mesh.vertex_groups}

def delete_unused_bones(armature, all_vertex_groups):
    # Delete bones that aren't in the list
    bpy.ops.object.mode_set(mode='EDIT')
    o = bpy.context.object
    b = armature.data.edit_bones[0]
    for bone in b.children_recursive:
        m = re.search(r'\.\d+$', bone.name)
        if m is not None:
           bone.name = bone.name.replace(m[0], "")
        if bone.name not in all_vertex_groups:
           print(f"Deleting bone {bone.name}")
           bpy.context.object.data.edit_bones.remove(bone)
    

def get_parent_armature(mesh):
    if mesh.parent and mesh.parent.type == 'ARMATURE':
        return mesh.parent
    return None

selected_objects = bpy.context.selected_objects
armature_selected = len(selected_objects) == 1 and selected_objects[0].type == 'ARMATURE'
meshes_selected = meshes_selected = len(selected_objects) > 0 and all(obj.type == 'MESH' for obj in selected_objects)

if armature_selected:
    armature = selected_objects[0]
    bone_names = {bone.name for bone in armature.data.bones}
    for mesh in (child for child in armature.children if child.type == 'MESH'):
        delete_vertex_groups_without_weights(mesh)
        delete_vertex_groups_without_corresponding_bone(mesh, bone_names)
    vertex_groups = get_all_vertex_groups(armature)
    delete_unused_bones(armature, vertex_groups)
    

if meshes_selected:
    for mesh in selected_objects:        
        armature = get_parent_armature(mesh)        
        bone_names = {bone.name for bone in armature.data.bones}
        delete_vertex_groups_without_weights(mesh)
        delete_vertex_groups_without_corresponding_bone(mesh, bone_names)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    ob = bpy.data.objects.get(armature.name)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    
    vertex_groups = get_all_vertex_groups(armature)        
    delete_unused_bones(armature, vertex_groups)
    
