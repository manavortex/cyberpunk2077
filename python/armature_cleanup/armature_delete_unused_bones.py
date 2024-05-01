import bpy

# Delete unused bones (without vertices rigged to them) from the armature

# Gather the names of all vertex groups for all children
all_vertex_groups = set()
armature = bpy.context.active_object

def cleanup_armature():
    
    for mesh in bpy.context.scene.objects:
        if mesh.type == 'MESH' and mesh.parent == armature:

            # Check and delete vertex groups with no vertices assigned
            for group in mesh.vertex_groups:
                print(group)
                if not any(vg.group == mesh.vertex_groups[vg.group].index for v in mesh.data.vertices for vg in v.groups):
                    mesh.vertex_groups.remove(mesh.vertex_groups[group])
            
            all_vertex_groups.update(mesh.vertex_groups.keys())    

def delete_unused_bones():    
    # Delete bones that aren't in the list
    for bone in armature.data.bones:
        if bone.name not in all_vertex_groups:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            bpy.ops.object.mode_set(mode='OBJECT')

# Run the cleanup function
cleanup_armature()

print(all_vertex_groups)
delete_unused_bones()
