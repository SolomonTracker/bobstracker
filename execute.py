""" CLI stuff """

import sys
import numpy as np
from processing import package_box, get_signers, gen_signatures
import pickle

def __main__():
    args = sys.argv
    order = args[1]

    FUNCS.get(order.lower(), failureCLI)(args[2:])

    return

def generateCLI(args):
    rng = np.random.default_rng()
    
    signatures = gen_signatures(rng, 600*300, 100, len(args))

    with open("signatures.bob", "wb") as output:
        pickle.dump(signatures, output)

def failureCLI(_args):
    print("CLI Failure")

FUNCS = {"generate": generateCLI}

if __name__ == "__main__":
    __main__()

