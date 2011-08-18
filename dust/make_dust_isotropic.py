from hyperion.dust import IsotropicSphericalDust
from hyperion.util.constants import pi

import numpy as np
np.seterr(all='ignore')

from hyperion.util.integrate import interp1d_log10

data = np.loadtxt('optSi.dat', comments=';', dtype=[('wav', float), ('csca', float), ('cext', float)])

# Convert SI to CGS
data['cext'] *= 1.e4
data['csca'] *= 1.e4

size = 0.12 * 1.e-4
density = 3.6
wav = data['wav']
kappa = data['cext'] / (4. * pi / 3. * size**3. * density)
albedo = data['csca'] / data['cext']

kappa_i = interp1d_log10(wav, kappa)
albedo_i = interp1d_log10(wav, albedo)

wav = np.logspace(np.log10(wav.min()), np.log10(wav.max()),1000)
wav[0] = 0.12
wav[-1] = 2000.

kappa = kappa_i(wav)
albedo = albedo_i(wav)

d = IsotropicSphericalDust(wav, kappa, albedo)
d.optical_properties._extrapolate(1.e-3, 1.e5)
d.plot('pascucci_dust_isotropic.png')
d.write('pascucci_dust_isotropic.hdf5')
