import sys
import os
import shutil
import re

from gbx_py.src.parser import parse_file
from gbx_py.export_obj import transform_pos
from gbx_py.src.utils.math import quaternion_from_matrix
from construct import Container

import configparser


def error(msg):
    print(msg)
    if sys.stdin.isatty():
        input()
    exit(1)

def config(file):
    conf = {}
    for l in open(file, "rt").readlines():
        l = l.strip()
        if not l or l.startswith("#") or l.startswith(";") or "=" not in l:
            continue
        l = l.split("=", 1)
        k = l[0].strip(" \"'").lower()
        v = l[1].strip(" \"'\n")
        conf[k] = v
    return conf


def get_tm_user_dir(nadeoini):
    nadeo = configparser.ConfigParser()
    nadeo.read(nadeoini)
    return re.sub("\{userdocs\}", re.escape(os.path.expanduser("~") + "\\Documents\\") , nadeo["Trackmania"]["UserDir"], flags=re.IGNORECASE)


def find_case_insensitive_path(parent_dir, file_name):
    target_name = file_name.casefold()
    for entry in os.listdir(parent_dir):
        if entry.casefold() == target_name:
            return os.path.join(parent_dir, entry)
    return None


RENAME_FILES = {"SkinDiffuse.dds":    "Skin_D.dds",
                "DiffuseDirty.dds":   "Skin_DirtMask.dds", # maybe naming error from some custom skin i found
                "SkinDirty.dds":      "Skin_DirtMask.dds",
                "DetailsDiffuse.dds": "Details_B.dds", # roughness wont work without copying alpha layer and using _R, same with wheels
                "DetailsIllum.dds":   "Details_I.dds",
                "DetailsDirty.dds":   "Details_DirtMask.dds",
                "WheelsDiffuse.dds":  "Wheels_B.dds",
                "WheelsDirty.dds":    "Wheels_DirtMask.dds"}

def rename_files(skin_dir):
    for k, v in RENAME_FILES.items():
        path_from = find_case_insensitive_path(skin_dir, k)
        path_to = os.path.join(skin_dir, v)
        if path_from and os.path.isfile(path_from):
            print(f"Rename {path_from} -> {path_to}")
            shutil.move(path_from, path_to)
    print()






def visual(vis):
    vertices = []
    normals = []
    uvs = []
    indices = []
    
    if "body" in vis:
        if vis.body[0x0900600F].texCoords:
            for t in vis.body[0x0900600F].texCoords[0].tex_coords:
                uvs.append(t.uv)
        else:
            return None # fix
            
        for v in vis.body[0x0902C004].vertices:
            vertices.append(v.position)
            normals.append(v.normal)
        
        indices = vis.body[0x0906A001].indexBuffer[0x9057000].indices
        
        return [vertices, normals, uvs, indices]
    else:
        return None



def obj(name ,verts, norms, uvs, indices, obj_verts=[0]):
    out = f"o {name}\n\n"
    
    for v in verts:
        v = transform_pos(v, None, None, True)
        out += f"v {v[0]} {v[1]} {v[2]}\n"
    out += "\n"
    
    for n in norms:
        n = transform_pos(n, None, None, True)
        out += f"vn {n[0]} {n[1]} {n[2]}\n"
    out += "\n"
    
    for uv in uvs:
        out += f"vt {uv.x} {uv.y}\n"
    out += "\n"
    
    tot = obj_verts[0]
    
    for i in range(0, len(indices), 3):
        f = tot + indices[i] + 1, tot + indices[i+1] + 1, tot + indices[i+2] + 1
        out += f"f {f[0]}/{f[0]}/{f[0]} {f[1]}/{f[1]}/{f[1]} {f[2]}/{f[2]}/{f[2]}\n"
    
    obj_verts[0] = tot + len(verts)
    
    return out



def extract_skin_meshes(skin_dir):
    obj_path = os.path.abspath(os.path.join(skin_dir, "temp.obj"))
    
    py_out = open("./drunub/blenderimports.py", "rt").read() # nefarious things are occurring
    py_out += "for o in D.objects: D.objects.remove(o)\n"
    py_out += f"bpy.ops.wm.obj_import(filepath=r'{obj_path}')\n\n"
    obj_out = ""
    obj_verts = [0]
    
    lod_files = [find_case_insensitive_path(skin_dir, "MainBodyVeryHigh.solid.gbx"),
                 find_case_insensitive_path(skin_dir, "MainBodyHigh.solid.gbx"),
                 find_case_insensitive_path(skin_dir, "MainBody.solid.gbx")]
    
    lod = 0
    
    for fn in lod_files:
        if fn and os.path.isfile(fn):
            print(f"\n\nExtracting {fn}...\n")
            lod += 1
            data = parse_file(fn)
            parts = data.body[0x9005011].tree.body[0x904f006].children
            
            for part in parts:
                part_name = part.body[0x904f00d].name
                loc = part.body[0x904f01a].loc
                
                vis = visual(part.body[0x904f016].visual)
                obj_mesh_name = f"{part_name}_Lod{lod}"
                print(obj_mesh_name + " ", end="", flush=True)
                
                if vis:
                    obj_out += obj(obj_mesh_name, *vis, obj_verts)
                else:
                    py_out += f"bpy.context.collection.objects.link(bpy.data.objects.new('{obj_mesh_name}', None))\n"
                
                if loc:
                    q = quaternion_from_matrix(loc)
                    py_out += f"D.objects['{obj_mesh_name}'].location = ({loc.TX}, {-loc.TZ}, {loc.TY})\n"
                    py_out += f"D.objects['{obj_mesh_name}'].rotation_mode = 'QUATERNION'\n"
                    py_out += f"D.objects['{obj_mesh_name}'].rotation_quaternion = Quaternion(({q.w}, {q.x}, {-q.z}, {q.y}))\n"
    
    py_out += "\n" + open("./drunub/boner.py", "rt").read()
    
    fbx_path = os.path.abspath(os.path.join(skin_dir, "MainBody.fbx"))
    py_out += f"bpy.ops.export_scene.fbx(filepath=r'{fbx_path}', add_leaf_bones=False)\n"
    py_out += f"bpy.ops.wm.quit_blender()\n"
    
    
    open(os.path.join(skin_dir, "temp.obj"),"wt").write(obj_out)
    open(os.path.join(skin_dir, "temp.py"), "wt").write(py_out)
    print("\n")


