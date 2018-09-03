import os
import math
from PIL import Image
#from Crypto.Cipher import AES

class StringTooLongException(Exception):
    pass

class ImageIsEncryptedError(Exception):
    pass

class InvalidPassphraseError(Exception):
    pass

def str2bin(message):       
    binary = bin(int.from_bytes(message, 'big'))
    return binary[2:]

def bin2str(binary):
    n = int(binary, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')

def encode(filename, message, passphrase=None):
    image = Image.open(filename)

    data = list(image.getdata())
    first_byte = list(data[0])

    if passphrase is None:
        first_byte[1] &= 254

    else:
        first_byte[1] |= 1

        if len(passphrase) == 16 | len(passphrase) == 24 | len(passphrase) == 32:
            raise InvalidPassphraseError

        suite = AES.new(passphrase)
        message = suite.encrypt(message)
        print(message)

    binary = str2bin(message)

    if (len(binary) % 8 != 0):
        binary = '0'*(8 - ((len(binary)) % 8)) + binary
    
    ratio = len(binary) / (len(data) * 3)
    if ratio < 1:
        bits = 1
    elif 1 <= ratio < 2:
        bits = 2
    elif 2 <= ratio < 4:
        bits = 4
    elif 4 <= ratio < 8:
        bits = 8
    else:
        raise StringTooLongException

    length_bytes = int(8 / bits)
    length = bin(len(binary))[2:]
    length = '0'*(24 - len(length)) + length

    first_byte[0] = first_byte[0] & (2**7 - 2**(bits-1))
    data[0] = tuple(first_byte)

    for byte in range(1, length_bytes + 1):
        pixel = list(data[byte])

        pixel[0] >>= bits
        pixel[0] <<= bits
        pixel[0] |= int('0b' + length[3*bits*(byte - 1):3*bits*(byte - 1)+bits], 2)

        pixel[1] >>= bits
        pixel[1] <<= bits
        pixel[1] |= int('0b' + length[3*bits*(byte - 1)+bits:3*bits*(byte - 1)+2*bits], 2)

        pixel[2] >>= bits
        pixel[2] <<= bits
        pixel[2] |= int('0b' + length[3*bits*(byte - 1)+2*bits:3*bits*(byte - 1)+3*bits], 2)
        
        data[byte] = tuple(pixel)

    img_index = 1 + length_bytes
    index = 0
    
    while (index < len(binary)):
        pixel = list(data[img_index])
        
        pixel[0] >>= bits
        pixel[0] <<= bits
        pixel[0] |= int('0b' + binary[index:index+bits], 2)
        index += bits

        if index < len(binary):
            pixel[1] >>= bits
            pixel[1] <<= bits
            pixel[1] |= int('0b' + binary[index:index+bits], 2)
            index += bits

        if index < len(binary):
            pixel[2] >>= bits
            pixel[2] <<= bits
            pixel[2] |= int('0b' + binary[index:index+bits], 2)
            index += bits

        data[img_index] = tuple(pixel)
        img_index += 1

    image.putdata(data)
    image.save(os.path.dirname(filename) + '/coded-' + os.path.basename(filename), 'PNG')

    return len(binary)


def decode(filename, passphrase=None):
    image = Image.open(filename)
    data = list(image.getdata())
    binary = ''

    if (data[0][1] % 2 == 1) and (passphrase is None):
        raise ImageIsEncryptedError

    if passphrase is not None and not (len(passphrase) == 16 | len(passphrase) == 24 | len(passphrase) == 32):
        raise InvalidPassphraseError

    bits = bin(data[0][0])[::-1].index('1') + 1
    length_bytes = int(8 / bits)

    size = ''

    for byte in range(1, length_bytes + 1):
        pixel = data[byte]
        size += format(pixel[0], '#010b')[-bits:]
        size += format(pixel[1], '#010b')[-bits:]
        size += format(pixel[2], '#010b')[-bits:]

    size = int('0b' + size, 2)
    count = 0

    while (count * bits * 3 < size):
        pixel = data[1 + length_bytes + count]
        binary += format(pixel[0], '#010b')[-bits:]
        binary += format(pixel[1], '#010b')[-bits:]
        binary += format(pixel[2], '#010b')[-bits:]

        count += 1

    binary = binary[:size]
    binary = bin2str(binary)

    if (data[0][1] % 2 == 1):
        suite = AES.new(passphrase)
        binary = suite.decrypt(binary)

    return binary


def hide_img(filename, copy_as):
    image = Image.open(filename)

    width, height = image.size
    
    if width <= 1280 and height <= 768:
        pass

    elif width/height >= 640/384:
        height *= (1280/width)
        width = 1280

    else:
        width *= (768/height)
        height = 768

    width, height = int(width), int(height)
    image = image.resize((width, height), Image.ANTIALIAS)
    
    data = list(image.getdata())
    given = list(copy_as.getdata())

    for index in range(len(data)):
        pixel = list(data[index])

        if given[index] == (0, 0, 0):
            pixel[0] &= 254
            pixel[1] &= 254
            pixel[2] &= 254

        elif given[index] == (255, 0, 0):
            pixel[0] |= 1
            pixel[1] &= 254
            pixel[2] &= 254

        elif given[index] == (0, 255, 0):
            pixel[0] &= 254
            pixel[1] |= 1
            pixel[2] &= 254

        elif given[index] == (0, 0, 255):
            pixel[0] &= 254
            pixel[1] &= 254
            pixel[2] |= 1

        elif given[index] == (255, 255, 0):
            pixel[0] |= 1
            pixel[1] |= 1
            pixel[0] &= 254

        elif given[index] == (128, 0, 128):
            pixel[0] |= 1
            pixel[1] &= 254
            pixel[2] |= 1

        elif given[index] == (255, 125, 0):
            pixel[0] &= 254
            pixel[1] |= 1
            pixel[2] |= 1

        elif given[index] == (255, 255, 255):
            pixel[0] |= 1
            pixel[1] |= 1
            pixel[2] |= 1

        pixel = tuple(pixel)
        data[index] = pixel

    image.putdata(data)
    image.save(os.path.dirname(filename) + '/coded-' + os.path.basename(filename), 'PNG')


def unhide_img(filename):
    image = Image.open(filename)
    data = list(image.getdata())

    new = Image.new('RGB', (image.width, image.height), '#FFFFFF')
    l = []

    for pixel in data:
        string = str(pixel[0] & 1) + str(pixel[1] & 1) + str(pixel[2] & 1)
        if string == '000':
            l.append((0, 0, 0))

        elif string == '100':
            l.append((255, 0, 0))

        elif string == '010':
            l.append((0, 255, 0))

        elif string == '001':
            l.append((0, 0, 255))

        elif string == '110':
            l.append((255, 255, 0))

        elif string == '101':
            l.append((128, 0, 128))

        elif string == '011':
            l.append((255, 125, 0))

        else:
            l.append((255, 255, 255))

    new.putdata(l)
    
    return new
    

if __name__ == '__main__':

##    import timeit
##    print(timeit.timeit('''

    file = open('sherlock.txt', mode='rb')

    print(encode('E:\\Python\\Steganography\\img.png', file.read()))
    print(str(decode('E:\\Python\\Steganography\\coded-img.png'))[:1000])

##    ''', open(__file__).read(), number=1))
