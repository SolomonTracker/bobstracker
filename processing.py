"""
Utils para firmar y generar firmas
"""

from PIL import Image
import numpy as np
from random import randint

def test():
    rng = np.random.default_rng()

    # open test image
    pic = Image.open("test.png")
    w, h = pic.size
    pic_arr = np.array(pic, dtype=np.uint8).reshape(-1)

    # generate signature
    signature = gen_signatures(rng, w*h, w, 1, ["WhoCares"])[0]
    
    # sign image
    pic_arr_signed = sign_image(pic_arr, signature[0]).reshape(h, w)
    pic_signed = Image.fromarray(pic_arr_signed, )

    # save it
    pic_signed.save("out_test.png")
    
    return

def sign_image(image, signature):
    """
    image: in array form [uint8]
    signature: hashmap( (j: int) -> bool )
    """
    
    return np.array([x if signature.get(j, 0) == 0 else 0 for j, x in enumerate(image)], dtype=np.uint8)

def check_signature(image, signature) -> bool:
    """
    image: in array form [uint8]
    signature: hashmap( (j: int) -> bool )
    """

    return True

def gen_signatures(rng, max_range, sign_len, ammount, names):
    """
    rng: np.random.default_rng()
    max_range: maximum index
    sign_len: ammount of index per signature
    ammount: number of signatures
    names: Ex ["AWS", "Vitol", ···]
    """

    numbers = np.arange(0, max_range)

    list_of_indexes = [sorted(rng.choice(numbers, size=sign_len, replace=False)) for _ in range(ammount)]

    return [ ({j:randint(0, 1) for j in i}, names[L]) for L, i in enumerate(list_of_indexes)]


if __name__ == "__main__":
    test()
    
