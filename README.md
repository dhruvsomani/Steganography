# Steganography

This repository contains simple code to encode bytes data into any .PNG image using Python and the PIL library.

The most important code is in the `main.py` file which includes functions `encode` and `decode`.

`encode` takes in path to an image file and a text message and creates a new file with the the text hidden in it.
`decode` takes in path to an image file and spits out the data encoded in it.
