"""
Settings and helpers shared by the scripts that set up the Hyperion models
for the Pascucci et al. (2004) benchmark. Snakemake adds the directory of
each script to the module search path, so these can be imported directly.
"""

import numpy as np

from hyperion.model import Model
from hyperion.util.constants import rsun, pi, sigma, au

# Star:
#
# T_star = 5,800K
# R_star = R_sun (but treated as a point source)

STAR_RADIUS = 1.  # = 1 cm (i.e. point source)
STAR_TEMPERATURE = 5800.
STAR_LUMINOSITY = 4. * pi * rsun ** 2 * sigma * STAR_TEMPERATURE ** 4

# The wavelengths at which the benchmark SEDs are defined

WAVELENGTHS = np.loadtxt('paper_results/wavelengths.txt')

# SEDs:
#
# i = 12.5, 42.5 and 77.5 degrees, in a 3000 AU aperture

SED_THETA = np.array([12.5, 42.5, 77.5])
SED_PHI = np.array([30.0, 30.0, 30.0])


def set_star(star):
    """
    Set the properties of the star on a source (or the star of an
    AnalyticalYSOModel).
    """
    star.radius = STAR_RADIUS
    star.temperature = STAR_TEMPERATURE
    star.luminosity = STAR_LUMINOSITY


def model_from_temperatures(filename):
    """
    Set up a model with the geometry, density and temperatures of an
    existing run, for computing SEDs without recomputing the temperatures.
    """
    m = Model()
    set_star(m.add_spherical_source())
    m.use_geometry(filename)
    m.use_quantities(filename)
    m.set_n_initial_iterations(0)
    set_output(m)
    return m


def set_output(m):
    """
    Don't copy the input (which includes the dust properties) into the
    output file, which instead links to the input file, so that the output
    files are small enough to keep. The SEDs can be read from the output file
    alone, but the input file is needed to read the grid and temperatures.
    """
    m.set_copy_input(False)


def add_sed(m):
    """
    Add the peeled SEDs for the benchmark viewing angles.
    """
    image = m.add_peeled_images()
    image.set_viewing_angles(SED_THETA, SED_PHI)
    image.set_image_size(1, 1)
    image.set_image_limits(-1500. * au, 1500. * au, -1500. * au, 1500. * au)
    image.set_aperture_range(1, 1500. * au, 1500. * au)
    return image


def set_binned_sed_wavelengths(image, step):
    """
    Bin the SED for non-monochromatic runs in bins evenly spaced in
    log(wavelength), with a width of step (in dex), covering the benchmark
    wavelengths. The benchmark wavelengths are not evenly spaced, so the
    plotting script interpolates the binned SEDs to them.
    """
    n_bins = int(np.ceil(np.log10(WAVELENGTHS[-1] / WAVELENGTHS[0]) / step)) + 1
    log_centre = 0.5 * np.log10(WAVELENGTHS[-1] * WAVELENGTHS[0])
    half_width = 0.5 * n_bins * step
    image.set_wavelength_range(n_bins, 10 ** (log_centre - half_width), 10 ** (log_centre + half_width))
