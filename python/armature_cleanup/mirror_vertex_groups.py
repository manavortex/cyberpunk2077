import bpy
active_object = bpy.context.active_object

vertex_groups = active_object.vertex_groups[:]

# we'll end up with duplicate names if we rename right away
for vertex_group in vertex_groups:
    if vertex_group.name.startswith('r_'):
        vertex_group.name = vertex_group.name.replace('r_', 'REPLACEME_l_', 1)
        continue
    if vertex_group.name.startswith('l_'):
        vertex_group.name = vertex_group.name.replace('l_', 'REPLACEME_r_', 1)
        continue
    if vertex_group.name.startswith('Left'):
        vertex_group.name = vertex_group.name.replace('Left', 'REPLACEME_Right', 1)
        continue
    if vertex_group.name.startswith('Right'):
        vertex_group.name = vertex_group.name.replace('Right', 'REPLACEME_Left', 1)
        continue
    
for vertex_group in vertex_groups:
    vertex_group.name = vertex_group.name.replace('REPLACEME_', '')
    continue
    
