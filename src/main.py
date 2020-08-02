import sys
from random import randint
from noise import pnoise2
import numpy as np
from PIL import Image
from math import sqrt

#sea_level = randint(500, 550)
sea_level = 550
#beach_level = randint(145, 155)
beach_level = 600
#ground_level = randint(155, 170)
ground_level = 675
#mountain_level = randint(170, 180)
mountain_level = 800

PLANET_DIAMETER = 1000

# Size of image data
shape = (PLANET_DIAMETER, PLANET_DIAMETER, 3)

# Parameters for noise function
octaves = 6
freq = 32.0 * octaves
b = randint(0, 500)

colorgen = lambda: [[randint(0, 255) for i in range(3)] for i in range(5)]


colors = colorgen()


"""
Changes the noise value returned from pnoise from the default
of being between -1 and 1, to being a color value that can be
displayed for the current generated planet. Color values are generated
using the set of colors provided and the 

PARAMS:
    x, y -> int: Position of value in image
    val -> float: value to be processed
    masks -> tuple of lambdas: masks in the form of lambda
                               functions to be applied to the value.
                               masks must follow the standard form of
                               of taking the following parameters:
                               (x, y, val) in that order.

"""
def convert_noise(x, y, val, masks):

    # "magnitude" of noise at this point
    normalval = val * 500 + 500

    # Apply user masks to terrain before coloring
    for mask in masks:
        normalval = mask(x, y, normalval)

    # Color of the area of land represented at this point
    colorval = [0, 0, 0]
    
    if normalval == -1:
        colorval = [0, 0, 0]
    elif normalval <= sea_level:
        colorval = colors[0]
    elif normalval <= beach_level:
        colorval = colors[1]
    elif normalval <= ground_level:
        colorval = colors[2]
    elif normalval <= mountain_level:
        colorval = colors[3]
    else:
        colorval = colors[4]
    
    
    return colorval


####################
#                  #
#  MASK FUNCTIONS  #
#                  #
####################

"""
Applies a transformation to the point that increases the value of
a point given its distance from the equator. This is used to simulate
poles on a planet.

CURRENT IMPLEMENTATION: Using a polynomial equation as a multiplication factor

Previously I was adding a value to the noise based on distance. By changing
to a multiplication, if a value is very small it will still be proportionally
small after the transformation is applied. This means that polar caps on the
planets are encouraged, but the noise comes through a little better, allowing
for polar lakes and low-lands
"""
def caps_mask(x, y, val):
    return val * ((abs(y - 500) ** 4 / 62500000000) + 1)

"""
Applies a circular mask to the image to make it look like a planet
instead of a flat map.
"""
def world_mask(x, y, val):
    if (sqrt((x - 500) ** 2 + (y - 500) ** 2) >= 500):
        return -1
    return val

# Initialize output image data
landscape = np.zeros(shape)

# Generate noise and process it into planet image
for i in range(1, shape[0] + 1):
    for j in range(shape[1]):
        landscape[i - 1, j] = convert_noise(j, i,
                    pnoise2(i/freq, j/freq, octaves, 0.45, base=b),
                    [caps_mask, world_mask]
                    )

# Process and output image using PIL
planet = Image.fromarray(np.uint8(landscape))
planet.show()
planet.save("planet.jpg")