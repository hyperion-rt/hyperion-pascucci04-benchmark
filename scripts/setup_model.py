# Set up one of the Pascucci et al. (2004) benchmark models, which computes the
# temperatures and the SEDs at the benchmark wavelengths (in monochromatic
# mode). The disk mass and grid geometry come from the Snakemake wildcards,
# and the settings that differ between profiles come from config.yaml and are
# passed in by the Snakefile.

import numpy as np

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import pi, au, msun

from common import WAVELENGTHS, set_star, add_sed, set_output

settings = snakemake.params.settings
geometry = snakemake.wildcards.geometry

# Disk masses (in solar masses) for each of the model names

DISK_MASSES = {'1.1e-07': 1.113838e-7,
               '1.1e-06': 1.113838e-6,
               '1.1e-05': 1.113838e-5,
               '1.1e-04': 1.113838e-4}

disk_mass = DISK_MASSES[snakemake.wildcards.mass]

m = AnalyticalYSOModel()

set_star(m.star)

# Disk:
#
# rho(r,z) = rho_0 * (r/rd)^-1.0 * exp(-pi * (z/(2*h(r)))^2)
# h(r) = zd * (r/rd)^1.125
# rd = rmax / 2.
# zd = rmax / 8.
# r_in = 1AU, r_out = 1000AU
# Sharp vertical edges in cylindrical polar coordinates
# Disk mass (dust!) = 1.1e-7, 1.1e-6, 1.1e-5, 1.1e-4

disk = m.add_flared_disk()
disk.p = 0.125
disk.beta = 1.125
disk.mass = disk_mass * msun
disk.rmin = 1. * au
disk.rmax = 1000. * au
disk.h_0 = 125 * au * np.sqrt(2. / pi)
disk.r_0 = 500 * au
# disk.cylindrical_inner_rim = False

# Dust:
#
# Spherical grains, 1 micron, 3.5g/cm^3

disk.dust = 'dust/pascucci_dust_isotropic.hdf5'

image = add_sed(m)
image.set_wavelength_range(len(WAVELENGTHS), 1, len(WAVELENGTHS))

m.set_raytracing(True)
m.set_n_initial_iterations(settings['n_initial_iterations'])
m.set_convergence(True, percentile=99., absolute=2., relative=1.02)

if geometry == 'sph':
    m.set_spherical_polar_grid_auto(*settings['grid'], 1, rmax=1300.*au)
else:
    m.set_cylindrical_polar_grid_auto(*settings['grid'], 1)

m.set_monochromatic(True, wavelengths=WAVELENGTHS)

m.set_n_photons(**settings['n_photons'])

set_output(m)

m.write(snakemake.output[0])
