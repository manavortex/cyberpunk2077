import bpy
import os
from pathlib import Path
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb

def import_glb_to_collections():
    # Get the directory of the current .blend file
    blend_path = bpy.data.filepath
    if not blend_path:
        print("Error: Please save the .blend file first")
        return
    
    base_dir = os.path.dirname(blend_path)
    
    bpy.ops.object.select_all(action='DESELECT')
    
    for collection in bpy.data.collections:
      
        # Check for matching GLB file
        glb_path = os.path.join(base_dir, f"{collection.name}.glb")
        if not os.path.exists(glb_path):
            print(f"No matching GLB found for {collection.name}")
            continue
                
        # Select all visible mesh objects in the collection
        for obj in collection.all_objects:
            if obj.type == 'MESH' and obj.visible_get() and obj.name != "sculptme":
                obj.select_set(True)
        
        # If we found meshes to import
        if bpy.context.selected_objects:
            # Import the GLB file (will replace selected objects)
            try:
                            
                export_cyberpunk_glb(
                    bpy.context,
                    glb_path,
                    export_poses = False,
                    export_visible = False,
                    limit_selected = True,
                    static_prop = False
                )
                print(f"Successfully imported {glb_path}")
            except Exception as e:
                print(f"Failed to export {glb_path}: {str(e)}")
        
        # Deselect for next iteration
        bpy.ops.object.select_all(action='DESELECT')

if __name__ == "__main__":
    import_glb_to_collections()
