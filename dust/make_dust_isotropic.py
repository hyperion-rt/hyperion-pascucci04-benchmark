import numpy as np

from hyperion.dust import IsotropicDust
from hyperion.util.constants import pi, c

from hyperion.util.integrate import interp1d_fast_loglog

data = np.loadtxt('optSi.dat', comments=';', dtype=[('wav', float), ('csca', float), ('cext', float)])

# Convert SI to CGS
data['cext'] *= 1.e4
data['csca'] *= 1.e4

size = 0.12 * 1.e-4
density = 3.6
wav = data['wav']
nu = c / (wav * 1.e-4)
kappa = data['cext'] / (4. * pi / 3. * size**3. * density)
albedo = data['csca'] / data['cext']

wav_new = np.logspace(np.log10(wav.min()), np.log10(wav.max()),1000)
wav_new[0] = 0.12
wav_new[-1] = 2000.

kappa = interp1d_fast_loglog(wav, kappa, wav_new)
albedo = interp1d_fast_loglog(wav, albedo, wav_new)
nu = c / (wav_new * 1.e-4)

d = IsotropicDust(nu[::-1], albedo[::-1], kappa[::-1])
d.optical_properties.extrapolate_wav(1.e-3, 1.e5)
d.plot('pascucci_dust_isotropic.png')
d.write('pascucci_dust_isotropic.hdf5')
