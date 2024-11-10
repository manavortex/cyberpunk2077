import bpy

# will put left and right vertex groups next to each other for easier weight painting

def reorder_vertex_groups(obj):
    """Reorders vertex groups so that each 'Right' group is directly below the corresponding 'Left' group."""
    vgroups = obj.vertex_groups
    left_to_right = {}
    ordered_groups = []

    # Map each "Left" group to its corresponding "Right" group
    for vg in vgroups:
        if vg.name.startswith("Left"):
            corresponding_right = vg.name.replace("Left", "Right", 1)
            if corresponding_right in vgroups:
                left_to_right[vg.index] = vgroups[corresponding_right].index
        if vg.name.startswith("l_"):
            corresponding_right = vg.name.replace("l_", "r_", 1)
            if corresponding_right in vgroups:
                left_to_right[vg.index] = vgroups[corresponding_right].index

    # Add any remaining groups that do not start with "Left"
    for vg in vgroups:
        if vg.name not in ordered_groups:
            ordered_groups.append(vg.name)

    # Re-create groups in the desired order
    current_weights = {v.index: {vg.group: vg.weight for vg in v.groups} for v in obj.data.vertices}
    obj.vertex_groups.clear()  # Remove all existing groups

    # Re-add vertex groups in the desired order
    for group_name in ordered_groups:
        new_group = obj.vertex_groups.new(name=group_name)
        for v_idx, weights in current_weights.items():
            if group_name in weights:
                new_group.add([v_idx], weights[group_name], 'REPLACE')

    print("Vertex groups reordered.")

# Ensure only one mesh is selected
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    reorder_vertex_groups(obj)
else:
    print("Please select a mesh object.")
