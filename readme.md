
# tm-pf-converter
sorry for tha wait, i been workin on other stuff :0)

this will take a tm2 3d skin and convert it (mostly) to tm2020

the mesh of the skin MUST have been made with tm2's nadeoimporter and not the tmnf meshes (a lot of "tm2" skins are actually tmnf)

i wrote most of this quite a while ago, i cant remember how some of it works, this is more a proof of concept at this point, this thing is mega jank, it WILL break, dont expect it to work with every tm2 skin, use at own risk

i probably wont be continuing much with this or maybe at all

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

if the skin uses pack files, it WONT work (you need the .solid.mesh files), pack files can be extracted by equipping the skin and looking inside the memory/temp folder in tm2 openplanet, i created a tutorial: https://www.youtube.com/watch?v=ZFK3acudNMA

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

it doesn't automatically remove unused textures,,, you probably want to delete damage or dirt textures if you need to save space

fakeshad doesn't work atm, but i will consider adding

**optional texture stuff**

i might consider automating this part at some point

at the moment, because the textures are only renamed, roughness only works on the skin texture and not details or wheels. this is because the _D texture suffix (which uses the same format as tmnf/tm2) only works on the skin material. for details and wheels, you will need to copy the alpha channel of Details/Wheels_B to the red channel of Details/Wheels_R. green channel is for metallic which i usually fill white. if you want to control the metallic of the skin texture, you can also follow the same method (and rename Skin_D to Skin_B)

also iirc, for some reason Skin_B doesn't work without Skin_R, but Wheels and Details are fine without.... so like:

Skin_D 
OR
Skin_B and Skin_R

Details_B and optionally Details_R
Wheels_B and optionally Wheels_R

more details here:
tm2 texture format: https://doc.maniaplanet.com/customization/importer/import-a-car-skin (under 'Texture sheets' section)
tm2020 texture format: https://wiki.trackmania.io/en/content-creation/texture-mods

i'm sure there's some other textures i've missed, maybe normals, but maybe they can also simply be renamed
