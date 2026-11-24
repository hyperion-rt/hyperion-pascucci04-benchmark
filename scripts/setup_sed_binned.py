# Set up a run that computes the SEDs for one of the Pascucci et al. (2004)
# benchmark models in the normal (non-monochromatic) mode, re-using the
# temperatures from the model. The SEDs are binned in wavelength (in bins of
# 0.02 dex), and the plotting script interpolates them to the benchmark
# wavelengths. The settings that differ between profiles come from
# config.yaml and are passed in by the Snakefile.

from common import model_from_temperatures, add_sed, set_binned_sed_wavelengths, write

settings = snakemake.params.settings

m = model_from_temperatures(snakemake.input.model)

image = add_sed(m)
set_binned_sed_wavelengths(image, 0.02)

m.set_raytracing(True)

m.set_n_photons(**settings['n_photons'])

write(m, snakemake.output[0])
