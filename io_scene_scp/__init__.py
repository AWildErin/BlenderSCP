import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from bpy.utils import register_class
from bpy.utils import unregister_class

from . import import_rmesh

bl_info = {
    "name" : "BlenderSCP",
    "author" : "AWildErin",
    "description" : "A plugin to allow importing rmesh files",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Import-Export"
}

class ImportRMesh(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.rmesh"
    bl_label = "Import rmesh"
    bl_description = "Import one or more rmesh files"
    bl_options = {'PRESET'}

    filename_ext = ".rmesh"
    filter_glob: StringProperty(default="*.rmesh", options={'HIDDEN'})

    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        result = import_rmesh.load(
            self, context, **self.as_keywords(ignore=("filter_glob", "files")))
        if result:
            self.report({'INFO'}, 'rmesh has been loaded')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'Failed to load rmesh')
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return True

def menu_func_rmesh_import(self, context):
    self.layout.operator(ImportRMesh.bl_idname, text="RMesh (.rmesh)")

def register():
    bpy.utils.register_class(ImportRMesh)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_rmesh_import)


def unregister():
    bpy.utils.unregister_class(ImportRMesh)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_rmesh_import)

if __name__ == "__main__":
    register()
