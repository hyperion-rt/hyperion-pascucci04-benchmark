# Set up a run that computes the SEDs for one of the Pascucci et al. (2004)
# benchmark models at the benchmark wavelengths in monochromatic mode,
# re-using the temperatures from the model. The settings that differ between
# profiles come from config.yaml and are passed in by the Snakefile.

from common import WAVELENGTHS, model_from_temperatures, add_sed, write

settings = snakemake.params.settings

m = model_from_temperatures(snakemake.input.model)

image = add_sed(m)
image.set_wavelength_range(len(WAVELENGTHS), 1, len(WAVELENGTHS))

m.set_raytracing(True)

m.set_monochromatic(True, wavelengths=WAVELENGTHS)

m.set_n_photons(**settings['n_photons'])

write(m, snakemake.output[0])
