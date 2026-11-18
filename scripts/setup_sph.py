import numpy as np

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import rsun, pi, sigma, au, msun

# The settings that differ between the full and fast runs come from the
# profile selected in config.yaml, and are passed in by the Snakefile.

settings = snakemake.params.settings

# Disk masses (in solar masses) for each of the model names

DISK_MASSES = {'1.1e-07': 1.113838e-7,
               '1.1e-06': 1.113838e-6,
               '1.1e-05': 1.113838e-5,
               '1.1e-04': 1.113838e-4}

disk_mass = DISK_MASSES[snakemake.wildcards.mass]

m = AnalyticalYSOModel()

# Star:
#
# T_star = 5,800K
# R_star = R_sun
# M_star = M_sun

m.star.radius = 1. # = 1 cm (i.e. point source)
m.star.temperature = 5800.
m.star.luminosity = 4. * pi * rsun**2 * sigma * 5800.**4

# Disk:
#
# rho(r,z) = rho_0 * (r/rd)^-1.0 * exp(-pi * (z/(2*h(r)))^2)
# h(r) = zd * (r/rd)^1.125
# rd = rmax / 2.
# zd = rmax / 8.
# r_in = 1AU, r_out = 1000AU\
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

# SEDs/Images:
#
# cos(i) = 0.05 to 0.95 in steps of 0.1
# Images computed at 1 micron
# 251 pixels/900 AU across, at 140 pc

theta = np.array([12.5, 42.5, 77.5])
phi = np.array([30.0, 30.0, 30.0])

image = m.add_peeled_images()
image.set_viewing_angles(theta, phi)
image.set_image_size(1, 1)
image.set_image_limits(-1500.*au, 1500.*au, -1500.*au, 1500.*au)
image.set_aperture_range(1, 1500.*au, 1500.*au)
image.set_wavelength_range(61, 1, 61)

m.set_raytracing(True)
m.set_n_initial_iterations(settings['n_initial_iterations'])
m.set_convergence(True, percentile=99., absolute=2., relative=1.02)

m.set_spherical_polar_grid_auto(*settings['grid'], 1, rmax=1300.*au)

wavelengths = np.loadtxt('paper_results/wavelengths.txt')
m.set_monochromatic(True, wavelengths=wavelengths)

m.set_n_photons(**settings['n_photons'])

m.write(snakemake.output[0])
