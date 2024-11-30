""" CLI stuff """

import sys
import numpy as np
from processing import package_box, get_signers, gen_signatures
import pickle
from PIL import Image
import subprocess
import graphviz

image_orig = Image.open("cert_0.png")
w_orig, h_orig = image_orig.size
image_orig = np.array(image_orig).reshape(-1)

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

def packageCLI(args):
    with open("signatures.bob", "rb") as f:
        signatures_by_name = pickle.load(f)

    name, fp = args
    
    sign = signatures_by_name[name]
    image = np.array(Image.open(fp)).reshape(-1)
    image_signed = package_box(image_orig, image, [sign])
    image_signed_to_save = Image.fromarray(image_signed.reshape(h_orig, w_orig))
    image_signed_to_save.save(f"cert_{int(fp[-5])+1}.png")

    # dot = graphviz.Digraph(comment='Package Life Graph')
    # dot.node('A')
    # dot.node('B')
    # dot.render(".graph.gv")

    signers = get_signers(image_orig, image_signed, signatures_by_name.values(), signatures_by_name.keys())

    update_database(signers)

    subprocess.run(["xdg-open", f"cert_{int(fp[-5])+1}.png"])

def cleanCLI(_args):
    with open("signers.db", "wb") as f:
        pickle.dump([[]], f)

def failureCLI(_args):
    print("CLI Failure")

def update_database(signers):
    try:
        with open("signers.db", "rb") as f:
            signers_db = pickle.load(f)
    except:
        signers_db = [[]]
        with open("signers.db", "wb") as f:
            pickle.dump(signers_db, f)

    for L, entry in enumerate(signers_db):
        coinc = [comp for comp in signers if comp not in entry]
        if len(coinc) == 1:
            signers_db[L].append(coinc[0])

    dot = graphviz.Digraph(comment='Package Life Graph')
    for entry in signers_db:
        dot.node(entry[0])
        for L, name in enumerate(entry[1:]):
            dot.node(name)
            dot.edge(entry[L], name)

    dot.render(".graph.gv")
    
    with open("signers.db", "wb") as f:
        pickle.dump(signers_db, f)

FUNCS = {"generate": generateCLI, "package": packageCLI, "clean": cleanCLI}

if __name__ == "__main__":
    __main__()

