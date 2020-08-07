import sys
import random
from noise import pnoise2
import numpy as np
from PIL import Image
from math import sqrt
import time


sea_level = random.randint(450, 600)

beach_level = random.randint(550, 650)
beach_level = beach_level if beach_level <= sea_level else beach_level + 51

#ground_level = randint(155, 170)
ground_level = random.randint(650, 725)
ground_level = ground_level if ground_level <= beach_level else ground_level + 2
#mountain_level = randint(170, 180)
mountain_level = random.randint(700, 950)
mountain_level = mountain_level if mountain_level <= ground_level else mountain_level + 26

PLANET_DIAMETER = 1000

# Size of image data
shape = (PLANET_DIAMETER, PLANET_DIAMETER, 3)

# Parameters for noise function
octaves = 6
freq = 32.0 * octaves
b = random.randint(0, 100)
offset_x = random.randint(0, 10000)
offset_y = random.randint(0, 10000)

colorgen = lambda: [[random.randint(0, 255) for i in range(3)] for i in range(5)]


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
for i in range(1, shape[0] + 1): # For some reason, values of 0 on the i
                                 # axis causes the Perlin function to only
                                 # output values of 0, for some reason the
                                 # domain starts at 1 for this axis.
    for j in range(shape[1]):
        landscape[i - 1, j] = convert_noise(j, i,
                    pnoise2((i + offset_x)/freq, (j + offset_y)/freq, octaves, 0.45, base=b),
                    [caps_mask, world_mask]
                    )

# Process and output image using PIL
planet = Image.fromarray(np.uint8(landscape))
planet.show()

# Add seconds since epoch to beginning of filename to ensure unique name
filename = ".\\results\\" + str(time.time()) + "_planet.jpg"

planet.save(filename)