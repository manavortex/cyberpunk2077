import bpy

def create_and_bind_surface_deform(target_obj):
    """Creates and binds a Surface Deform modifier for all visible meshes that are not the target object."""
    # Iterate over all objects in the scene
    for obj in bpy.context.scene.objects:
        # Check if the object is a visible mesh and not the target object
        if obj.type == 'MESH' and obj != target_obj and obj.visible_get():
            # Create a Surface Deform modifier
            surf_deform_mod = obj.modifiers.new(name="Surface Deform", type='SURFACE_DEFORM')
            surf_deform_mod.target = target_obj

            # Bind the Surface Deform modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.surfacedeform_bind(modifier=surf_deform_mod.name)

            print(f"Created and bound 'Surface Deform' modifier for '{obj.name}' to '{target_obj.name}'.")

def main():
    """Main function to create and bind Surface Deform modifier."""
    # Get the currently selected mesh
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if len(selected_meshes) != 1:
        print("Please select exactly one mesh object to serve as the target.")
        return

    target_obj = selected_meshes[0]

    create_and_bind_surface_deform(target_obj)

if __name__ == "__main__":
    main()
