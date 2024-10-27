import bpy

# this script will add a shrinkwrap modifier to your currently selected object to each other visible object in your blend file

def create_and_setup_shrinkwrap(target_obj):
    """Creates and configures a Shrinkwrap modifier for all visible meshes that are not the target object."""
    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is a visible mesh and not the target object
        if obj.type == 'MESH' and obj != target_obj and obj.visible_get():
            # Create a Shrinkwrap modifier
            shrinkwrap_mod = obj.modifiers.new(name="Shrinkwrap", type='SHRINKWRAP')
            shrinkwrap_mod.target = target_obj
            shrinkwrap_mod.wrap_method = 'NEAREST_SURFACEPOINT'
            shrinkwrap_mod.offset = 0.0001
            shrinkwrap_mod.use_negative_direction = False  # Only affect above surface
            shrinkwrap_mod.use_positive_direction = True

            print(f"Created 'Shrinkwrap' modifier for '{obj.name}' with target '{target_obj.name}'.")

    
def switch_to_layout_view():
    for screen in bpy.data.screens:
        if screen.name == "Layout":
            bpy.context.window.screen = screen
            break


def main():
    """Main function to create and configure Shrinkwrap modifiers."""
    # Get the currently selected mesh
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if len(selected_meshes) != 1:
        print("Please select exactly one mesh object to serve as the target.")
        return

    target_obj = selected_meshes[0]

    create_and_setup_shrinkwrap(target_obj)
    switch_to_layout_view()
    

if __name__ == "__main__":
    main()
