import bpy

def reorder_vertex_groups(obj):
    """Reorders vertex groups in 'Left-Right' pairs and maintains vertex weights."""
    
    vgroups = obj.vertex_groups
    group_weights = {}

    # Store weights by group name
    for vgroup in vgroups:
        group_weights[vgroup.name] = {v.index: g.weight for v in obj.data.vertices for g in v.groups if g.group == vgroup.index}

    # Create ordered list of group names with Left-Right pairs
    ordered_group_names = []
    for name in sorted(group_weights.keys()):
        if name.startswith("Left"):
            ordered_group_names.append(name)
            corresponding_right = name.replace("Left", "Right", 1)
            if corresponding_right in group_weights:
                ordered_group_names.append(corresponding_right)
        if name.startswith("l_"):
            ordered_group_names.append(name)
            corresponding_right = name.replace("l_", "r_", 1)
            if corresponding_right in group_weights:
                ordered_group_names.append(corresponding_right)

    # Add any remaining unpaired groups
    for name in group_weights.keys():
        if name not in ordered_group_names:
            ordered_group_names.append(name)

    # Clear existing vertex groups
    bpy.ops.object.mode_set(mode='OBJECT')
    for vgroup in list(vgroups):
        vgroups.remove(vgroup)

    # Recreate vertex groups in the new order with stored weights
    for name in ordered_group_names:
        new_group = vgroups.new(name=name)
        for v_idx, weight in group_weights[name].items():
            new_group.add([v_idx], weight, 'REPLACE')

    print("Vertex groups reordered successfully.")

# Run on the active object
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    reorder_vertex_groups(obj)
else:
    print("Please select a mesh object.")
