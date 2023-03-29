import bpy, math, bmesh
import os, struct, array

from . import binaryreader

def load(self, context, filepath=""):
    
    # Model settings
    hasTriggerBox = False
    noColl = False
    roomScale = 0.25

    ob = bpy.context.object
    scene = bpy.context.scene
    model_name = os.path.splitext(os.path.basename(filepath))[0]

    print(filepath)

    # todo: Move to a separate class when I figure out how blender stuff works
    # todo: Move the binary reading stuff to some helper classes like our C++ reader
    file = open(filepath, "rb")

    # We get the first index because unpack will always return a tuple.
    #hdrLength = struct.unpack("i", file.read(4))[0]
    #header = file.read(hdrLength)
    #decodedHeader = header.decode()

    header = binaryreader.readString(file)

    # Are we a valid rmesh file?
    if (not header.startswith("RoomMesh")):
        print("Invalid RMesh file")
        return False

    surfaceCount = binaryreader.readInt(file)

    materials = []
    for i in range(surfaceCount):
    #if True:
        #i = 0
        mesh = bpy.data.meshes.new("Surface " + str(i))
        obj = bpy.data.objects.new("Node " + str(i), mesh)

        materialIndex = len(materials)
        for j in range(2):
            blendType = binaryreader.readChar(file)
            if (blendType != 0):
                textureName = binaryreader.readString(file)
                
                # Ignore lightmap material, todo: Revisit this maybe? Add it back?
                if textureName == "" or textureName.endswith("lm1.png"):
                    continue

                foundExistingMaterial = False                
                # todo: Is there a better method here?
                if (len(materials) > 0 and not textureName.endswith("_lm1.png")):
                    for mat in materials:
                        if mat.name == textureName:
                            materialIndex = materials.index(mat)
                            foundExistingMaterial = True
                            break

                if (not foundExistingMaterial):
                    material = bpy.data.materials.new(textureName)
                    material.use_nodes = True
                    bsdf = material.node_tree.nodes["Principled BSDF"]
                    bsdf.inputs["Specular"].default_value = 0.4
                    texImage = material.node_tree.nodes.new("ShaderNodeTexImage")
                    material.node_tree.links.new(bsdf.inputs["Base Color"], texImage.outputs["Color"])

                    materials.append(material)

        vertCount = binaryreader.readInt(file)
        verts = []
        uvs = []
        rgb = []
        for j in range(vertCount):
            # Flip x so the mesh is correct
            x = -binaryreader.readFloat(file) * roomScale
            y = binaryreader.readFloat(file) * roomScale
            z = binaryreader.readFloat(file) * roomScale
            verts.append((x,y,z))

            # We have to flip uvs in blender for some reason
            u = binaryreader.readFloat(file)
            v = -binaryreader.readFloat(file)
            uvs.append((u,v))

            # unk1,2
            binaryreader.readFloat(file)
            binaryreader.readFloat(file)

            r = binaryreader.readChar(file)
            g = binaryreader.readChar(file)
            b = binaryreader.readChar(file)
            rgb.append((r,g,b))

            
        triCount = binaryreader.readInt(file)
        tris = []
        for j in range(triCount):
            p1 = binaryreader.readInt(file) + len(verts) - vertCount
            p2 = binaryreader.readInt(file) + len(verts) - vertCount
            p3 = binaryreader.readInt(file) + len(verts) - vertCount
            tris.append([p1,p2,p3])
        
        mesh.from_pydata(verts, [], tris)

        # Setup materials
        uvlist = [i for poly in mesh.polygons for vidx in poly.vertices for i in uvs[vidx]]
        mesh.uv_layers.new().data.foreach_set("uv", uvlist)

        mesh.materials.append(materials[materialIndex])

        for j in range(triCount):
            mesh.polygons[j].material_index = 0
        
        context.scene.collection.objects.link(obj)

        # Rooms are on their side, lets rotate them back
        obj.rotation_euler[0] = math.radians(90)

    return True
