
import struct
from tkinter import filedialog
import bsp_tool
import tkinter as tk
import os
import sys

root = tk.Tk()
root.withdraw()

#   removes useless vector & array nonsense from outputted data
def fixVector(v):
    
    v = str(v).split("(")[1]
    v = v.split(")")[0]
    
    return v

bsp_path = ""

#   parse commandline args for automation
args = str(sys.argv).split(",")

#   combined all args so paths with spaces can work
if len(args) > 1:
    superarg = ""
    for a in args[1:]:
        superarg += str(a)
    arg_path = superarg
    bsp_path = arg_path.replace("'", "").replace("]", "")[2:]
    print(bsp_path)

#   non automated workflow
if bsp_path == "":
    print("Please input path to bsp file:")
    bsp_path = filedialog.askopenfilename(
        title="Select a bsp",
        filetypes=[(f"Titanfall Bsp files", f"*.bsp")]
        )

#   load bsp
bsp = bsp_tool.load_bsp(bsp_path)

#   props
propCount = bsp.GAME_LUMP.sprp.props._length;

print (str(propCount) + " props...")

#   use mprt instead, better compatibility.
#   if ppl really need lights they can use io_import_rbsp
makeMprt = True

#   MPRT
if makeMprt :

    output_name = os.path.basename(bsp_path)
    output_name = os.path.splitext(output_name)[0]

    print("Outputting as MPRT (" + str(output_name) + ")")

    with open(output_name + ".mprt", "wb") as f:

        typeCheck = 0x7472706D

        #   header
        f.write(struct.pack("I", int(str(typeCheck))))
        f.write(struct.pack("I", int(str(propCount))))  #   I don't know what this one is supposed to be or if it's even used
        f.write(struct.pack("I", int(str(propCount))))

        #   prop data
        for p in bsp.GAME_LUMP.sprp.props :

            #   model name
            name = str(bsp.GAME_LUMP.sprp.model_names[p.model_name])
            splitName = name.split("/")
            name = splitName[len(splitName) - 1].split(".")[0]
            f.write(struct.pack(f"{len(name) + 1}s", str(name).encode('utf-8')))

            #   position
            for pos in fixVector(str(p.origin)).split(", "):
                f.write(struct.pack("f", float(pos)))

            #   rotation
            rots = fixVector(str(p.angles)).replace("x: ", "").replace("y: ", "").replace("z: ", "").split(", ")
            f.write(struct.pack("f", float(rots[2])))
            f.write(struct.pack("f", float(rots[0]) * -1))
            f.write(struct.pack("f", float(rots[1])))

            #   scale
            f.write(struct.pack("f", float(p.scale)))


#   MAPDATA
else :
    output = "#-props(mdl,pos,rot,scl)#\n"

    #   prop data
    for p in bsp.GAME_LUMP.sprp.props :
        output += str(bsp.GAME_LUMP.sprp.model_names[p.model_name]) + "|"
        output += fixVector(str(p.origin)) + "|"
        output += fixVector(str(p.angles)) + "|"
        output += str(p.scale) + "\n"

    #   lights
    output +="#-lights(pos,dir,type,col,exp,rad)#\n"

    print(str(len(bsp.WORLD_LIGHTS)) + " lights (zoo wee mama)")

    #   light data
    for l in bsp.WORLD_LIGHTS:
        output+=fixVector(str(l.origin)) + "|"
        output+=fixVector(str(l.normal)) + "|"
        output+=str(l.type) + "|"
        output+=fixVector(str(l.intensity)) + "|"
        output+=str(l.exponent) + "|"
        output+=str(l.radius) + "\n"

    output_name = os.path.basename(bsp_path)
    output_name = os.path.splitext(output_name)[0]

    text_file = open(output_name + ".mapdata", "w")
    text_file.write(output)
    text_file.close()

#   entities
#output +="#entities#\n"

#print(str(len(bsp.ENTITIES)) + " entities (kowabunga)")

#   entity data
#for e in bsp.ENTITIES:
#    output+=str(e) + "\n"

#   generate output file
