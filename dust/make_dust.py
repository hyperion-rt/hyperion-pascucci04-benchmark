from hyperion.dust import MieXDust

import numpy as np
np.seterr(all='ignore')

d = MieXDust('pascucci_dust/pascucci')
d._extrapolate(1.e-3, 1.e5)
d.plot('pascucci_dust.png')
d.write('pascucci_dust.fits')
