import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb

# This script will do the following things:
# 1. Select an export folder
# 2. Ask you for a file extension (.glb for meshes, .morphtarget.glb otherwise)
# 3. Save your file
# 4. Switch to a backup file
# 5. Apply shapekeys (destructively)
# 6. Export all collections to the folder from step 1 (only meshes starting with "submesh_" will be considered
# 7. Open the original file from step 3


original_path = ""
export_folder = ""
export_file_extension = ""

# Helper to set collections visible (recursive)
def set_visible(coll):
    coll.hide_viewport = False
    coll.hide_render = False
    for child in coll.children:
        set_visible(child)

# Informational popup (optional)
def showPopup(title, message_):
    try:
        from ctypes import windll
        windll.user32.MessageBoxW(None, message_, title, 1)
    except:
        # Fallback no-op or Blender custom message fallback
        print(f"{title}: {message_}")


def detect_extension(folder):
    if not folder or not os.path.isdir(folder):
        raise ValueError("Export folder invalid")
     
    files = os.listdir(folder) 

    # Detect extensions for all collections
    extensions = set()
    for coll in bpy.data.collections:        
        full_name = ([f for f in files if f.startswith(coll.name)] or [None])[0]
        
        if not full_name:
            continue

        file_name, file_ext = os.path.splitext(full_name)
        extensions.add(file_ext)        
    
    if ".morphtarget.glb" in extensions:
        return ".morphtarget.glb"

    if len(extensions) == 1:
        # All matched the same extension: use it
        return extensions.pop()
    
    # Query file exception
    bpy.ops.wm.query_extension('INVOKE_DEFAULT')
    
   
    
# Operator to select export folder
class SelectExportFolderOperator(Operator, ExportHelper):
    bl_idname = "wm.select_export_folder"
    bl_label = "Select Export Folder"
    filename_ext = ""
    use_filter_folder = True

    directory: StringProperty(
        name="Export Folder",
        description="Choose the folder to export to",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    def execute(self, context):
        global original_path
        global export_file_extension
        global export_folder
        
        folder = self.directory
        if not folder:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}

        # Store selected folder globally for next operator usage
        export_folder = folder

        try:
           export_file_extension = detect_extension(folder)
        except Exception as exception:
            self.report({'ERROR'}, "Exception message: {}".format(exception))
            return { 'CANCELLED' }

        if not export_file_extension:
            self.report({'ERROR'}, "No file extension")
            return { 'CANCELLED' }            
               
        if not export_file_extension.startswith("."):
            export_file_extension = "." + export_file_extension         
         
        # Proceed to apply shapekeys and export
        return bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')


# Operator to detect or query file extension
class QueryExtensionOperator(Operator):
    bl_idname = "wm.query_extension"
    bl_label = "Detect or Query File Extension"

    user_extension: StringProperty(
        name="File Extension",
        description="Specify file extension for export (include dot, e.g. .glb)",
        default=".glb"
    )

    def execute(self, context):
        global original_path
        global export_file_extension
        global export_folder
        
        folder = export_folder
        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Export folder not set or invalid.")
            return {'CANCELLED'}


        # Multiple or no extensions found, prompt user
        ret = context.window_manager.invoke_props_dialog(self)
        if ret == {'FINISHED'}:
            export_file_extension = user_extension
        return ret


    def draw(self, context):
        layout = self.layout
        layout.label(text="Please enter file extension (with leading .)")
        layout.prop(self, "user_extension", text="File extension to use")

    def cancel(self, context):
        pass

    def modal(self, context, event):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Overriding invoke to ensure proper dialog use
        result = context.window_manager.invoke_props_dialog(self)
        return result

    def execute(self, context):
        export_file_extension = self.user_extension
        bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')
        return {'FINISHED'}
    
    
# Operator to backup, apply shapekeys, export, and restore original file
class BackupApplyExportOperator(Operator):
    bl_idname = "wm.backup_apply_export"
    bl_label = "Backup, Apply Shapekeys, Export, Restore"

    def execute(self, context):
        global original_path
        global export_file_extension
        global export_folder
                
        wm = context.window_manager
        original_path = bpy.data.filepath
        folder = export_folder
        file_extension = export_file_extension

        if not original_path:
            self.report({'ERROR'}, "Save the current file first before continuing.")
            return {'CANCELLED'}
        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Export folder not set or invalid.")
            return {'CANCELLED'}

        backup_path = original_path.rsplit(".", 1)[0] + "_EXPORT_TEMP.blend"

        # Save copy to backup path & switch to it
        bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=True)
        self.report({'INFO'}, f"Backup saved: {backup_path}")

        show_popup("Exporting collections", "Exporting collections - Blender will be unresponsive for a while")

        self.apply_shapekeys()

        # Export collections
        exported_count = 0
        for collection in bpy.data.collections:
            set_visible(collection)
            bpy.ops.object.select_all(action='DESELECT')
            selected_objs = []
            for obj in collection.objects:
                if obj.type == 'MESH' and obj.name.startswith('submesh_'):
                    obj.select_set(True)
                    selected_objs.append(obj)
            if not selected_objs:
                continue

            targetPath = os.path.join(folder, f"{collection.name}{file_extension}")
            print(f"Exporting: {targetPath}")
            export_cyberpunk_glb(
                bpy.context,
                targetPath,
                export_poses=False,
                export_visible=False,
                limit_selected=True,
                static_prop=False
            )
            exported_count += 1

       # Restore original file (switch back)
        bpy.ops.wm.open_mainfile(filepath=original_path)
        self.report({'INFO'}, "Restored original file.")

        showPopup('Shapekeys applied :)', f"Your shapekeys have been applied; {exported_count} collections have been exported to {file_extension}!")
        return {'FINISHED'}
    
    def apply_shapekeys(self):
        """Applies Surface Deform modifier to all mesh objects in the scene."""
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and any(mod.type == 'SURFACE_DEFORM' for mod in obj.modifiers):
                print(f"Applying Surface Deform to '{obj.name}'...")
                self.apply_surface_deform_to_shapekeys(obj)
            else:
                print(f"Skipping '{obj.name}': No Surface Deform modifier found.")                
                

    def delete_all_shapekeys(self, obj):
        """Deletes all shapekeys for a given object, iterating backwards."""
        if obj.data.shape_keys:
            for key_block in reversed(obj.data.shape_keys.key_blocks):
                obj.shape_key_remove(key_block)

    def replace_mesh_with_copy(self, mesh, mesh_copy):
        """Replaces the vertex data of the original mesh with the copied mesh."""
        # Delete all vertices from the original mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        bpy.context.view_layer.objects.active = mesh

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Replace the original mesh data with the copied mesh data
        mesh.data = mesh_copy.data.copy()

        # Remove the temporary mesh copy
        bpy.data.objects.remove(mesh_copy, do_unlink=True)
        print(f"Replaced vertex data for mesh '{mesh.name}'")

    def apply_surface_deform_to_shapekeys(self, mesh, modifier_name="Surface Deform"):
        """Applies Surface Deform modifier to shapekeys or replaces mesh data if no shapekeys exist."""
        bpy.context.view_layer.objects.active = mesh
        bpy.ops.object.mode_set(mode='OBJECT')

        # Check if the Surface Deform modifier exists
        surf_def_mod = mesh.modifiers.get(modifier_name)
        if not surf_def_mod:
            print(f"No Surface Deform modifier found on {mesh.name}.")
            return

        # Create a temporary copy of the mesh to apply the modifier
        mesh_copy = mesh.copy()
        mesh_copy.data = mesh.data.copy()
        bpy.context.collection.objects.link(mesh_copy)

        # Apply the Surface Deform modifier to the copy
        bpy.context.view_layer.objects.active = mesh_copy
        self.delete_all_shapekeys(mesh_copy)
        try:
            bpy.ops.object.modifier_apply(modifier=modifier_name)
        except Exception as e:
            print(f"Failed applying Surface Deform to mesh '{mesh.name}': {e}")
            bpy.data.objects.remove(mesh_copy, do_unlink=True)
            return

        if mesh.data.shape_keys:
            # Apply the deformed vertex positions to each shapekey
            deformed_verts = [v.co for v in mesh_copy.data.vertices]
            shape_keys = mesh.data.shape_keys.key_blocks
            for shapekey in shape_keys:
                mesh.active_shape_key_index = shape_keys.keys().index(shapekey.name)
                for i, vert in enumerate(mesh.data.vertices):
                    shapekey.data[i].co += deformed_verts[i] - vert.co       
            bpy.data.objects.remove(mesh_copy, do_unlink=True)
        else:
            # Replace the original mesh with the modified copy
            self.replace_mesh_with_copy(mesh, mesh_copy)

    
def register():
    bpy.utils.register_class(SelectExportFolderOperator)
    bpy.utils.register_class(QueryExtensionOperator)
    bpy.utils.register_class(BackupApplyExportOperator)

def unregister():
    bpy.utils.unregister_class(BackupApplyExportOperator)
    bpy.utils.unregister_class(QueryExtensionOperator)
    bpy.utils.unregister_class(SelectExportFolderOperator)
    
# ------------ main: run -------------
if __name__ == "__main__":
    register()
    bpy.ops.wm.select_export_folder('INVOKE_DEFAULT')
