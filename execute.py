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
    rng = np.random.default_rng()
    
    signatures = gen_signatures(rng, h_orig*w_orig, 100, len(args))

    signatures_by_name = {name:signatures[L] for L, name in enumerate(args)}

    with open("signatures.bob", "wb") as output:
        pickle.dump(signatures_by_name, output)

def newpackageCLI(args):
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)

    pk_id, trace = signers_db
    trace.append([])
    pk_id += 1
    signers_db = (pk_id, trace)

    with open("signers.db", "wb") as f:
        pickle.dump(signers_db, f)

    subprocess.run(["cp", ".orig.png", get_last_fp(signers_db)])

def packageCLI(args):
    with open("signatures.bob", "rb") as f:
        signatures_by_name = pickle.load(f)
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)

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

    subprocess.run(["xdg-open", get_last_fp(signers_db)])

def get_last_fp(signers_db):
    return f"pkg_{chr(ord('a')+signers_db[0])}_{len(signers_db[1][-1])}.png"

def cleanCLI(_args):
    with open("signers.db", "wb") as f:
        pickle.dump((-1, []), f)
        
    with open("signatures.bob", "wb") as output:
        pickle.dump({}, output)

def showdiffCLI(_args):
    with open("signers.db", "rb") as f:
        signers_db = pickle.load(f)
    image = np.array(Image.open(get_last_fp(signers_db)), dtype=np.uint8).reshape(-1)
    image_diff1 = np.array([0 if x == y else 255 for x, y in zip(image_orig, image)], dtype=np.uint8)
    image_diff1 = Image.fromarray(image_diff1.reshape(h_orig, w_orig))
    for _ in range(3):
        image_diff1 = image_diff1.filter(ImageFilter.MaxFilter(3))
    image_diff2 = image_diff1.filter(ImageFilter.MaxFilter(3))
    image_diff = (np.array(image_diff2) - np.array(image_diff1)).reshape(-1)
    image = np.array([x if y != 255 else 255 for x, y in zip(image, image_diff)], dtype=np.uint8)
    image = Image.fromarray(image.reshape(h_orig, w_orig))
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

FUNCS = {
    "generate": generateCLI,
    "newpackage": newpackageCLI,
    "package": packageCLI,
    "clean": cleanCLI,
    "showdiff": showdiffCLI
}

if __name__ == "__main__":
    __main__()

