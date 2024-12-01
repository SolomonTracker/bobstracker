""" CLI stuff """

import sys
import numpy as np
from processing import package_box, get_signers, gen_signatures
import pickle
from PIL import Image, ImageFilter
import subprocess
import graphviz

image_orig = Image.open(".orig.png")
w_orig, h_orig = image_orig.size
image_orig = np.array(image_orig, dtype=np.uint8).reshape(-1)

def __main__():
    args = sys.argv
    order = args[1]

    FUNCS.get(order.lower(), failureCLI)(args[2:])

    return

def generateCLI(args):
    if len(args) == 0:
        sponsors = ["AWS", "BOBST", "BMS", "Logitech", "AWS", "AXA", "UBS", "Vitol"] 
        print("Sponsors: "+', '.join(sponsors)+'.')
        generateCLI(sponsors)
    rng = np.random.default_rng()
    
    signatures = gen_signatures(rng, h_orig*w_orig, 100, len(args))

    signatures_by_name = {name:signatures[L] for L, name in enumerate(args)}

    with open("signatures.bob", "wb") as output:
        pickle.dump(signatures_by_name, output)

def newpackageCLI(_args):
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)

    pk_id, trace = signers_db
    trace.append([])
    pk_id += 1
    signers_db = (pk_id, trace)

    with open("signers.db", "wb") as f:
        pickle.dump(signers_db, f)

    subprocess.run(["cp", ".orig.png", get_last_fp(signers_db)])

def packageCLI(args, show_res = True):
    with open("signatures.bob", "rb") as f:
        signatures_by_name = pickle.load(f)
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)

    if signers_db[0] == -1:
        newpackageCLI([])

    name = args[0]
    
    sign = signatures_by_name[name]
    image = np.array(Image.open(get_last_fp(signers_db))).reshape(-1)

    signers_db[1][-1].append(name)
    
    image_signed = package_box(image_orig, image, [sign])
    image_signed_to_save = Image.fromarray(image_signed.reshape(h_orig, w_orig))
    image_signed_to_save.save(get_last_fp(signers_db))

    with open("signers.db", "wb") as f:
        pickle.dump(signers_db, f)
        
    update_database()

    if show_res:
        subprocess.run(["xdg-open", get_last_fp(signers_db)])

def get_last_fp(signers_db):
    return f"pkg_{chr(ord('a')+signers_db[0])}_{len(signers_db[1][-1])}.png"

def cleanCLI(_args):
    with open("signers.db", "wb") as f:
        pickle.dump((-1, []), f)
        
    with open("signatures.bob", "wb") as output:
        pickle.dump({}, output)

def showdiffCLI(_args):
    with open("signatures.bob", "rb") as f:
        signatures_by_name = pickle.load(f)
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)

    mask1 = np.zeros(h_orig*w_orig, dtype=np.uint8)
    for name in signers_db[1][-1]:
        for k in signatures_by_name[name]:
            if signatures_by_name[name][k] == 0:
                mask1[k] = 255
        
    mask1 = Image.fromarray(mask1.reshape(h_orig, w_orig))
    for _ in range(2):
        mask1 = mask1.filter(ImageFilter.MaxFilter(3))
    mask2 = mask1.filter(ImageFilter.MaxFilter(3))
    mask = (np.array(mask2) - np.array(mask1)).reshape(-1)
    
    image = np.array(Image.open(get_last_fp(signers_db)), dtype=np.uint8).reshape(-1)
    
    image_diff1 = np.array([0 if x == y else 255 for x, y in zip(image_orig, image)], dtype=np.uint8)
    image_diff1 = Image.fromarray(image_diff1.reshape(h_orig, w_orig))
    for _ in range(3):
        image_diff1 = image_diff1.filter(ImageFilter.MaxFilter(3))
    image_diff2 = image_diff1.filter(ImageFilter.MaxFilter(3))
    image_diff = (np.array(image_diff2) - np.array(image_diff1)).reshape(-1)
    
    image = np.array([[0xF9, 0x54, 0x54] if y == 255 else [0x0D, 0x92, 0xF4] if z == 255 else [x]*3 for (x, y), z in zip(zip(image, image_diff), mask)], dtype=np.uint8)
    image = Image.fromarray(image.reshape(h_orig, w_orig, -1))
    image.show()
    return

def failureCLI(_args):
    print("CLI Failure")

def update_database():
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)
        
    dot = graphviz.Digraph('Package Life Graph', filename=".graph.gv")
    for K, entry in enumerate(signers_db[1]):
        gdot = graphviz.Digraph(name=f"cluster_{K}")
        gdot.attr(styled="filled") 
        gdot.attr(color="lightgray")
        gdot.attr(label=f"Pkg {K}")
        gdot.node(f"{K}{0}", entry[0], shape="circle")
        for L, name in enumerate(entry[1:]):
            gdot.node(f"{K}{L+1}", name, shape="circle")
            gdot.edge(f"{K}{L}", f"{K}{L+1}")
        dot.subgraph(gdot)

    dot.render(".graph.gv")

def complexexampleCLI(_args):
    cleanCLI([])
    sponsors = ["AWS", "BOBST", "BMS", "Logitech", "AWS", "AXA", "UBS"] 
    print("Sponsors: "+','.join(sponsors)+'.')
    generateCLI(sponsors)
    newpackageCLI([]); print("Pkg a")
    packageCLI(["AWS"], False); print("	AWS packages")
    packageCLI(["BMS"], False); print("	BMS packages")
    packageCLI(["AWS"], False); print("	AWS packages")
    packageCLI(["Logitech"], False); print("	Logitech packages")
    packageCLI(["AXA"], True); print("	AXA packages")
    newpackageCLI([]); print("Pkg b")
    packageCLI(["UBS"], False); print("	UBS packages")
    packageCLI(["BOBST"], False); print("	BOBST packages")
    packageCLI(["AWS"], False); print("	AWS packages")
    packageCLI(["UBS"], True); print("	UBS packages")
    newpackageCLI([]); print("Pkg c")
    packageCLI(["Logitech"], False); print("	Logitech packages")
    packageCLI(["BMS"], True); print("	BMS packages")
    newpackageCLI([]); print("Pkg d")
    packageCLI(["BOBST"], False); print("	BOBST packages")
    packageCLI(["AXA"], False); print("	AXA packages")
    packageCLI(["UBS"], True); print("	UBS packages")
    subprocess.run(["xdg-open", ".graph.gv.pdf"])
    showdiffCLI([])

FUNCS = {
    "generate": generateCLI,
    "newpackage": newpackageCLI,
    "package": packageCLI,
    "clean": cleanCLI,
    "showdiff": showdiffCLI,
    "complexexample": complexexampleCLI
}

if __name__ == "__main__":
    __main__()

