""" CLI stuff """

import sys
import numpy as np
from processing import package_box, get_signers, gen_signatures
import pickle
from PIL import Image

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
    with open("signatures.bob", "wb") as f:
        signatures_by_name = pickle.load(f)

    name, fp = args
    
    sign = signatures_by_name[name]
    image = np.array(Image.open(fp)).reshape(-1)
    image_signed = package_box(image_orig, image, [sign])
    if image_signed == -1:
        failureCLI(0)
        return
    image_signed = Image.fromarray(image_signed.reshape(h_orig, w_orig))
    image_signed.save(f"cert_{int(fp[-5])+1}.png")

def failureCLI(_args):
    print("CLI Failure")

FUNCS = {"generate": generateCLI}

if __name__ == "__main__":
    __main__()

