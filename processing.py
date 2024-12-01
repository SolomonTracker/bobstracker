"""
Utils para firmar y generar firmas
"""

from PIL import Image
import numpy as np
from random import randint

def _test():
    rng = np.random.default_rng()

    # open test image
    pic = Image.open("test.png")
    w, h = pic.size
    pic_arr = np.array(pic, dtype=np.uint8).reshape(-1)

    # generate signature
    names = ["WhoCares#1", "WhoCares#2", "SomeoneDoes#1"]
    signature = gen_signatures(rng, w*h, w, len(names))
    
    # sign image
    # pic_arr_signed = sign_image(pic_arr, signature[0])
    pic_arr_signed = sign_image(pic_arr, signature[0])
    # assert (check_signature(pic_arr, pic_arr_signed, signature[0]))
    pic_signed = Image.fromarray(pic_arr_signed.reshape(h, w))

    # save it
    pic_signed.save("out_test.png")
    
    return

def test():
    rng = np.random.default_rng()

    ##### ORIG IMAG #####
    pic = Image.open("test.png")
    w, h = pic.size
    pic_arr = np.array(pic, dtype=np.uint8).reshape(-1)

    ##### SIGNATURES #####
    N_OF_IDXS = 200
    names = ["WhoCares#1", "WhoCares#2", "SomeoneDoes#1", "SomeoneDoes#2"]
    signature = gen_signatures(rng, w*h, N_OF_IDXS, len(names))

    return

def package_box(orig_image, image, signatures):
    usable_signature = signatures[0]
    for sign in signatures:
        if not check_signature(orig_image, image, sign):
            usable_signature = sign
            break

    return sign_image(image, usable_signature)

def get_signers(orig_image, image, signatures, names):
    return [name for name, sign in zip(names, signatures) if check_signature(orig_image, image, sign)]

def sign_image(image, signature):
    """
    image: in array form [uint8]
    signature: hashmap( (j: int) -> bool )
    """
    
    return np.array([x if signature.get(j, 0) == 0 else (int(x)+25)%256 for j, x in enumerate(image)], dtype=np.uint8)

def check_signature(orig_image, image, signature) -> bool:
    """
    image: in array form [uint8]
    signature: hashmap( (j: int) -> bool )
    """
    
    arr1 = [x for L, x in enumerate(sign_image(orig_image, signature)) if L in signature]
    arr2 = [x for L, x in enumerate(image) if L in signature]
    
    return arr1 == arr2

def gen_signatures(rng, max_range, sign_len, ammount):
    """
    rng: np.random.default_rng()
    max_range: maximum index
    sign_len: ammount of index per signature
    ammount: number of signatures
    """

    numbers = np.arange(0, max_range)

    list_of_indexes = [sorted(rng.choice(numbers, size=sign_len, replace=False)) for _ in range(ammount)]

    return [ {j:randint(0, 1) for j in i} for i in list_of_indexes ]


if __name__ == "__main__":
    test()
    
