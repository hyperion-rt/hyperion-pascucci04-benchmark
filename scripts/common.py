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

# Dust:
#
# Spherical grains, 1 micron, 3.5g/cm^3

DUST_FILE = 'dust/pascucci_dust_isotropic.hdf5'

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
    # The dust properties are taken from the dust file rather than from the
    # existing run, so that they can be linked to rather than copied when
    # writing the model (see write)
    m.use_quantities(filename, use_dust=False)
    m.dust = [DUST_FILE]
    m.set_n_initial_iterations(0)
    return m


def write(m, filename):
    """
    Write out a model, linking to the dust file rather than copying the dust
    properties into it, and without copying the input into the output file,
    which links to the input file instead (copying the input would also copy
    the dust properties, since these are followed through the link). The
    dust properties make up almost all of the size of the files otherwise, so
    this keeps both the input and output files small enough to keep. Reading
    the grid and temperatures from the output files requires the input files,
    and the dust file at the same location relative to them, which is the
    case within this repository.
    """
    m.set_copy_input(False)
    m.write(filename, copy=False)


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
