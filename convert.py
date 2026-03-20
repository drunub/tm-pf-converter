import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from drunub.dings import error, config, rename_files, extract_skin_meshes
from drunub.skinfix import fix_skin


OUT_EXTENSIONS = [".dds", ".mesh.gbx", ".txt", ".wav", ".ogg"]

WORK_TEMP_DIR = Path("./temp/")
OUT_DIR = Path("./out/")


def case_insensitive_path(path):
    path = Path(path)
    if path.exists():
        return path

    parent = path.parent
    if not parent.exists():
        return path

    wanted = path.name.casefold()
    for child in parent.iterdir():
        if child.name.casefold() == wanted:
            return child
    return path


def get_tm_user_dir(conf):
    value = conf.get("tmuserpath")
    if value:
        return Path(value)

    if os.name == "nt":
        return Path.home() / "Documents" / "Trackmania"

    error("Can't determine Trackmania user dir. Set TMUSERPATH in paths.ini")
    raise SystemExit(1)


def get_wine_prefix(tm_user_dir):
    parts = tm_user_dir.parts
    if "pfx" in parts:
        return Path(*parts[:parts.index("pfx") + 1])
    return None


def get_proton_appid(tm_user_dir):
    parts = tm_user_dir.parts
    if "compatdata" in parts:
        idx = parts.index("compatdata") + 1
        if idx < len(parts):
            return parts[idx]
    return None


def run_command(command, **kwargs):
    print("Running:", " ".join(str(part) for part in command))
    return subprocess.run(command, check=False, **kwargs)


def pick_skin_zip():
    qt_widgets = None
    try:
        from PySide6 import QtWidgets
        qt_widgets = QtWidgets
    except ImportError:
        error("Missing input skin zip and PySide6 is not installed for the file picker")
        raise SystemExit(1)

    app = qt_widgets.QApplication.instance() or qt_widgets.QApplication([])
    file_path, _ = qt_widgets.QFileDialog.getOpenFileName(
        None,
        "Select a TM2 skin zip",
        str(Path.cwd()),
        "Zip files (*.zip);;All files (*)",
    )
    if not file_path:
        error("No input skin zip selected")
    return Path(file_path)


conf = config("./paths.ini")

blender = Path(conf.get("blender", "./blender/blender.exe"))
tm2020_config = conf.get("tm2020")
if not tm2020_config:
    error("Missing TM2020 path in paths.ini")

tm2020 = case_insensitive_path(tm2020_config)
tm_user_dir = get_tm_user_dir(conf)

ni_work_dir = tm_user_dir / "Work" / "Skins" / "temp"
ni_out_dir = tm_user_dir / "Skins" / "temp"

importer = case_insensitive_path(Path(tm2020) / "NadeoImporter.exe")

if not blender.is_file():
    error(f"Can't find Blender, nothing to do :0(\nCheck paths.ini or {blender}")

if not importer.is_file():
    error(f"Can't find NadeoImporter, check paths.ini or {importer}")

skin_zip_path = Path(sys.argv[1]) if len(sys.argv) >= 2 else pick_skin_zip()

print("Extracting skin...\n")

shutil.rmtree(WORK_TEMP_DIR, ignore_errors=True)
WORK_TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
ni_work_dir.mkdir(parents=True, exist_ok=True)
ni_out_dir.mkdir(parents=True, exist_ok=True)

with ZipFile(skin_zip_path, "r") as z:
    z.extractall(WORK_TEMP_DIR)


rename_files(WORK_TEMP_DIR)
extract_skin_meshes(WORK_TEMP_DIR)

blender_script = WORK_TEMP_DIR / "temp.py"
result = run_command([str(blender), "--background", "--factory-startup", "-P", str(blender_script)])
if result.returncode:
    error("Blender export failed :0(")


mainbody_fbx = case_insensitive_path(WORK_TEMP_DIR / "MainBody.fbx")
if not mainbody_fbx.is_file():
    error("MainBody.fbx missing, something failed :0(")

target_fbx = ni_work_dir / "MainBody.fbx"
target_mesh_params = ni_work_dir / "MainBody.MeshParams.xml"
target_mesh = ni_out_dir / "MainBody.Mesh.gbx"

shutil.move(mainbody_fbx, target_fbx)
shutil.copyfile("./drunub/export/MainBody.MeshParams.xml", target_mesh_params)

importer_command = [str(importer), "Mesh", r"Skins\temp\MainBody.fbx"]
importer_env = None

if os.name != "nt":
    protontricks = shutil.which("protontricks-launch")
    proton_appid = conf.get("proton_appid") or get_proton_appid(tm_user_dir)
    if protontricks and proton_appid:
        importer_command = [protontricks, "--appid", proton_appid, str(importer), "Mesh", r"Skins\temp\MainBody.fbx"]
    else:
        wine = shutil.which("wine") or shutil.which("wine64")
        if not wine:
            error("Can't find wine, needed to run NadeoImporter on Linux")
        importer_command = [wine, *importer_command]
        wine_prefix = get_wine_prefix(tm_user_dir)
        if wine_prefix:
            importer_env = os.environ.copy()
            importer_env["WINEPREFIX"] = str(wine_prefix)

result = run_command(importer_command, cwd=tm_user_dir, env=importer_env)
if result.returncode:
    error("NadeoImporter failed :0(")

target_mesh = case_insensitive_path(target_mesh)
if not target_mesh.is_file():
    error("NadeoImporter did not create MainBody.Mesh.gbx :0(")

fix_skin(target_mesh)

shutil.move(target_mesh, WORK_TEMP_DIR / "MainBody.mesh.gbx")

skin_name = skin_zip_path.name.rsplit(".", 1)[0]

out_files = []
for fn in WORK_TEMP_DIR.iterdir():
    for ext in OUT_EXTENSIONS:
        if fn.name.lower().endswith(ext):
            out_files.append(fn)
            break


with ZipFile(OUT_DIR / f"{skin_name} tm2020.zip", "w") as z:
    for fn in out_files:
        z.write(fn, arcname=fn.name)
    z.write("./drunub/export/drunub.txt", arcname="drunub.txt")


shutil.rmtree(WORK_TEMP_DIR, ignore_errors=True)
