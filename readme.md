
# tm-pf-converter
sorry for tha wait, i been workin on other stuff :0)

this will take a tm2 3d skin and convert it (mostly) to tm2020

the mesh of the skin MUST have been made with tm2's nadeoimporter and not the tmnf meshes (a lot of "tm2" skins are actually tmnf)

i wrote most of this quite a while ago, i cant remember how some of it works, this is more a proof of concept at this point, this thing is mega jank, it WILL break, dont expect it to work with every tm2 skin, use at own risk

i probably wont be continuing with this

pls maybe don't upload skins converted with this to maniapark etc, especially not without permission from original author, it probably isn't a perfect conversion

## requirements
- [gbx-py](https://github.com/schadocalex/gbx-py/tree/dev) (i included it to keep stuff simple)
- probably python 3.11 (or whatever gbx-py requires) [Python 3.14 needs compilation of lzo from source, which fails, 3.11 is recommended]
- tm2020 nadeoimporter (Install through Blendermania or download from [here](https://nadeo-download.cdn.ubi.com/trackmania/NadeoImporter_2022_07_12.zip). Unpack next to the games Trackmania.exe)
- blender (i think i tested it with blender 4.x, some older versions probably work. 5.0 and 5.1 don't work, download the portable release from [Here](https://download.blender.org/release/Blender4.5/))
- gbx-py requirements: ``python-lzo PySide6 Pillow construct``

### requirements on Linux
- TM2020 installed from Steam
- Protontricks (and specifically protontricks-launch)

## usage
it only takes a tm2 skin zip file as an input

if the skin uses pack files, it WONT work (you need the .solid.mesh files), pack files can be extracted by equipping the skin and  looking inside the memory/temp folder in openplanet in tm2 (i cant remember specifics)

it doesn't automatically remove unused textures,,, you probably want to delete damage or dirt textures if you need to save space


edit the ``paths.ini`` file (an example is included):
- ``BLENDER`` - blender executable path
- ``TM2020`` - nadeoimporter directory (usually the tm2020 path)
- ``TMUSERPATH`` - tm2020 user folder (where your skins etc go, Documents/Trackmania2020)

iirc, convert.py needs to be run from its directory, you can run convert.bat instead to do that:

example:

``convert.py tm2skin.zip``

``convert.bat tm2skin.zip``


alternatively, just drag the skin zip file onto convert.bat

if you are lucky, you will have a new zip file in the ``out`` folder, which you can copy straight to skins/models/carsport
