import bpy

def delete_all_shapekeys(obj):
    """Deletes all shapekeys for a given object, iterating backwards."""
    if obj.data.shape_keys:
        # Iterate over the shapekeys in reverse order
        for key_block in reversed(obj.data.shape_keys.key_blocks):
            obj.shape_key_remove(key_block)
            
def add_and_apply_lattice_modifier(lattice_name):
    # Get the lattice object
    lattice = bpy.data.objects.get(lattice_name)
    
    if lattice is None or lattice.type != 'LATTICE':
        print(f"Lattice object '{lattice_name}' not found or is not of type 'LATTICE'.")
        return

    # Iterate over all visible mesh objects
    for obj in bpy.context.visible_objects:
        if obj.type == 'MESH':
            delete_all_shapekeys(obj)
            # Check if a Lattice modifier already exists and remove it
            for modifier in obj.modifiers:
                if modifier.type == 'LATTICE' and modifier.object == lattice:
                    obj.modifiers.remove(modifier)
                    break

            # Add a new Lattice modifier
            lattice_mod = obj.modifiers.new(name="Lattice", type='LATTICE')
            lattice_mod.object = lattice

            # Set the mesh object as the active object
            bpy.context.view_layer.objects.active = obj

            # Apply the lattice modifier
            bpy.ops.object.modifier_apply(modifier=lattice_mod.name)
            print(f"Applied lattice modifier to '{obj.name}'")

# Define the lattice name
lattice_name = "Lattice"

# Run the function
add_and_apply_lattice_modifier(lattice_name)
