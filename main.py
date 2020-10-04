import os
from PIL import Image

class StringTooLongException(Exception):
	pass

class ImageIsEncryptedError(Exception):
	pass

def str2bin(message):       
	binary = bin(int.from_bytes(message, 'big'))
	return binary[2:]

def bin2str(binary):
	n = int(binary, 2)
	return n.to_bytes((n.bit_length() + 7) // 8, 'big')

def encode(filename, message):
	image = Image.open(filename)

	data = list(image.getdata())
	first_byte = list(data[0])

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
	image.save('coded-' + os.path.basename(filename), 'PNG')

	return len(binary)


def decode(filename):
	image = Image.open(filename)
	data = list(image.getdata())
	binary = ''

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

	return binary
	

if __name__ == '__main__':
	file = open('sherlock.txt', mode='rb')

	print(encode('img.png', file.read()))
	print(str(decode('coded-img.png'))[:1000])
