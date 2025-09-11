import bpy
import os
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from i_scene_cp77_gltf.exporters.glb_export import export_cyberpunk_glb
import time

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
    
    
def apply_modifiers(obj):
    """ applies all modifiers in order """
    # now uses object.convert to circumvent errors with disabled modifiers

    modifiers = obj.modifiers
    for modifier in modifiers:
        if modifier.type == 'SUBSURF':
            modifier.show_only_control_edges = False

    for o in bpy.context.scene.objects:
        o.select_set(False)

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.convert(target='MESH')    
    
def apply_shapekey(obj, sk_keep):
    """ deletes all shapekeys except the one with the given index """

    shapekeys = obj.data.shape_keys.key_blocks

    # check for valid index
    if sk_keep < 0 or sk_keep > len(shapekeys):
        return

    # remove all other shapekeys
    for i in reversed(range(0, len(shapekeys))):
        if i != sk_keep:
            obj.shape_key_remove(shapekeys[i])

    # remove the chosen one and bake it into the object
    obj.shape_key_remove(shapekeys[0])
    
def add_objs_shapekeys(destination, sources):
    """ takes an array of objects and adds them as shapekeys to the destination
    object """
    for o in bpy.context.scene.objects:
        o.select_set(False)

    for src in sources:
        src.select_set(True)

    bpy.context.view_layer.objects.active = destination
    bpy.ops.object.join_shapes()


def copy_object(obj, times=1, offset=0):
    """ copies the given object and links it to the main collection"""

    objects = []
    for i in range(0, times):
        copy_obj = obj.copy()
        copy_obj.data = obj.data.copy()
        copy_obj.name = obj.name + "_shapekey_" + str(i+1)
        copy_obj.location.x += offset*(i+1)

        bpy.context.collection.objects.link(copy_obj)
        objects.append(copy_obj)

    return objects   
    
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
        ret = context.window_manager.invoke_props_diaprint(self)
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
        result = context.window_manager.invoke_props_diaprint(self)
        return result

    def execute(self, context):
        export_file_extension = self.user_extension
        bpy.ops.wm.backup_apply_export('INVOKE_DEFAULT')
        return {'FINISHED'}
        
    def apply_modifiers(obj):
      """ applies all modifiers in order """
      # now uses object.convert to circumvent errors with disabled modifiers

      modifiers = obj.modifiers
      for modifier in modifiers:
          if modifier.type == 'SURFACE_DEFORM':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    
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

        # Save copy to backup path
        bpy.ops.wm.save_as_mainfile(filepath=backup_path, copy=False)
        self.report({'INFO'}, f"Backup saved: {backup_path}")

        
        error_count = 0
        processed_count = 0
        start_time = time.time()
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and any(mod.type == 'SURFACE_DEFORM' for mod in obj.modifiers):
                print(f"Applying Surface Deform to '{obj.name}'...")                
                result = self.apply_shapekeys(obj)
            
        shapekey_time = time.time() - start_time
        print(f"Shapekeys applied in {shapekey_time:.2f} seconds")

        showPopup("Exporting collections", "Exporting collections - Blender will be unresponsive for a minute or two.")

        # Export collections
        exported_count = 0
        export_start_time = time.time()
        
        # Pre-calculate which objects to export
        objects_to_export = []
        for collection in bpy.data.collections:
            set_visible(collection)
            collection_objects = []
            for obj in collection.objects:
                if obj.type == 'MESH' and obj.name.startswith('submesh_'):
                    collection_objects.append(obj)
            if collection_objects:
                objects_to_export.append((collection.name, collection_objects))

        # Export each collection
        for collection_name, objs in objects_to_export:
            # Deselect all first
            bpy.ops.object.select_all(action='DESELECT')
            
            # Select objects for this collection
            for obj in objs:
                obj.select_set(True)
            
            if not objs:
                continue

            targetPath = os.path.join(folder, f"{collection_name}{file_extension}")
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

        export_time = time.time() - export_start_time
        print(f"Exported {exported_count} collections in {export_time:.2f} seconds")

        # Restore original file
        bpy.ops.wm.open_mainfile(filepath=original_path)
        self.report({'INFO'}, "Restored original file.")

        total_time = time.time() - start_time
        showPopup('Shapekeys applied :)', 
                 f"Your shapekeys have been applied; {exported_count} collections exported in {total_time:.1f}s!")
        
        return {'FINISHED'}   
       
        
    def apply_shapekeys(self, obj):
        has_shapekeys = obj.data.shape_keys is not None and len(obj.data.shape_keys.key_blocks) > 0
        modifier = None
        for _modifier in obj.modifiers:
            if _modifier.type == 'SURFACE_DEFORM':
                modifier = _modifier

        if modifier is None:
            return {'FINISHED'}

        if not has_shapekeys:
            print("Object {} has no shapekeys, applying modifiers directly".format(obj.name))
            apply_modifiers(obj)
            return {'FINISHED'}

        # Get all shape keys including basis
        shape_keys = obj.data.shape_keys.key_blocks

        # Store original active shape key index
        original_active_index = obj.active_shape_key_index

        # Process each shape key except basis (index 0)
        for i in range(1, len(shape_keys)):
            shape_name = shape_keys[i].name

            # Duplicate object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()
            dup_obj = bpy.context.view_layer.objects.active

            # Remove all shapekeys except the current one
            dup_obj.shape_key_remove(all=True)
            # Recreate the basis shapekey (copied from current shape key)
            dup_obj.shape_key_add(name="Basis")
            dup_obj.shape_key_add(name=shape_name)
            # Copy current shape key vertex data into new shape key
            for i_vertex, coord in enumerate(shape_keys[i].data):
                dup_obj.data.shape_keys.key_blocks[shape_name].data[i_vertex].co = coord.co.copy()

            # Remove basis key to isolate the shape key as only deformation
            dup_obj.shape_key_remove(0)

            # Apply the Surface Deform modifier
            bpy.context.view_layer.objects.active = dup_obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)

            # Add the resulting mesh as a new shape key on original object
            # Select original object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            new_shape_key = obj.shape_key_add(name=shape_name + "_mod", from_mix=False)

            # Copy the geometry from the duplicate to the new shape key
            for v in range(len(obj.data.vertices)):
                new_shape_key.data[v].co = dup_obj.data.vertices[v].co

            # Delete the duplicate
            bpy.ops.object.select_all(action='DESELECT')
            dup_obj.select_set(True)
            bpy.ops.object.delete()

        # Now apply the modifier on the Basis shape key on original object
        # Remove all shape keys except Basis
        while len(obj.data.shape_keys.key_blocks) > 1:
            obj.shape_key_remove(1)

        # Apply Surface Deform modifier on the original mesh
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)

        # Basis shape key is now modified mesh base.

        # Restore original active shape key index if applicable
        if original_active_index < len(obj.data.shape_keys.key_blocks):
            obj.active_shape_key_index = original_active_index

        return {'FINISHED'}
    
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
