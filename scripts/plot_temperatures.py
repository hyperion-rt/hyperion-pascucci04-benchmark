import sys, os

prefix, output = sys.argv[1:3]

if not os.path.exists(prefix):
    raise Exception("No such directory: %s" % prefix)

if not os.path.exists(output):
    raise Exception("No such directory: %s" % output)

import numpy as np
from hyperion.util.constants import au, pi
import h5py
from hyperion.util.integrate import interp1d_fast, interp1d_fast_loglog
from hyperion.model import ModelOutput
from scipy.interpolate import RectBivariateSpline

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as mpl

# Set matplotlib preferences
mpl.rc('axes', titlesize='x-small')
mpl.rc('axes', labelsize='x-small')
mpl.rc('xtick', labelsize='xx-small')
mpl.rc('ytick', labelsize='xx-small')
mpl.rc('xtick.major', size=2)
mpl.rc('ytick.major', size=2)
mpl.rc('xtick.minor', size=1)
mpl.rc('ytick.minor', size=1)
mpl.rc('font', family='serif')
mpl.rc('axes', linewidth=0.5)
mpl.rc('patch', linewidth=0.5)
mpl.rc('text', usetex=True)
mpl.rc('ps', fonttype=42)

# Plotting settings

xmargin = 0.05
ymargin = 0.05

dx = 0.5 - 2 * xmargin
dy = (1.0 - 2 * ymargin) / 3.

def make_cuts(r, t, temperature):

    temperature_interp = RectBivariateSpline(r, t, temperature, kx=1, ky=1)

    rcyl = np.ones(100) * 2*au
    zcyl = np.linspace(-2*au, 2*au, 100)
    rsph1 = np.sqrt(rcyl*rcyl + zcyl*zcyl)
    tsph1 = np.arctan2(rcyl, zcyl)

    vertical = temperature_interp.ev(rsph1, tsph1)

    rsph2 = np.logspace(np.log10(1.*au), np.log10(1000*au), 100)
    tsph2 = np.ones(100) * np.radians(92.5)

    radial = temperature_interp.ev(rsph2, tsph2)

    return rsph2/au, radial, 90.-np.degrees(tsph1), vertical

def read_temperature(code, filename, nr, nt, skiprows=0):

    if code=='MC3D':

        f = open('paper_results/%s/100tau/%s' % (code, filename))
        f.readline()
        nr = int(f.readline().strip()) - 1
        nt = int(float(f.readline().strip()))
        t = np.array([np.radians(float(f.readline().replace('D',"E"))) for i in range(nt)]) + pi / 2.
        r = np.array([float(f.readline().replace('D',"E"))*au for i in range(nr)])
        temperature = np.array([float(f.readline().replace('D',"E")) for i in range(nr*nt)])
        temperature = temperature.reshape(nr, nt)

    elif code=='HYPERION':

        m = ModelOutput('%s/models/pascucci_1.1e-04.rtout' % prefix)
        grid = m.get_quantities()
        temperature = grid['temperature'][0].array[0, :, :]
        r = grid.r_wall
        t = grid.t_wall

        r = np.array(0.5*(r[1:] + r[:-1])).astype(np.float64)
        t = np.array(0.5*(t[1:] + t[:-1])).astype(np.float64)
        temperature = np.array(temperature).astype(np.float64).transpose()

    else:

        # Read in RADICAL results
        radical = np.loadtxt('paper_results/%s/100tau/%s' % (code, filename), skiprows=skiprows, dtype=[('r',float), ('t', float), ('temperature', float)])

        r = radical['r'].reshape(nr, nt)[:,0]
        t = radical['t'].reshape(nr, nt)[0,:]
        temperature = radical['temperature']

        if code is 'STEINRAY':
            r *= 100

        temperature = temperature.reshape(nr, nt)

    return make_cuts(r, t, temperature)

# Read in radial and vertical cuts in temperature
r_radical, radial_radical, t_radical, vertical_radical = read_temperature('RADICAL', 'dtemp.dat', 60, 62, skiprows=1)
r_steinray, radial_steinray, t_steinray, vertical_steinray = read_temperature('STEINRAY', 'tm.dat', 61, 61, skiprows=2)
r_mc3d, radial_mc3d, t_mc3d, vertical_mc3d = read_temperature('MC3D', 'tau-T100.020', 0, 0)
r_hyperion, radial_hyperion, t_hyperion, vertical_hyperion = read_temperature('HYPERION', 'temperature_005.fits.gz', 0, 0)

# Last hyperion value overlaps a bit over the edge of the disk, so the interpolated temperature is unreliable
r_hyperion, radial_hyperion = r_hyperion[:-1], radial_hyperion[:-1]

# Start figure
fig = mpl.figure(figsize=(6.5, 2.5))
artists = []

# RADIAL ABSOLUTE

xmin = xmargin
ymin = ymargin + dy

ax = fig.add_axes([xmin, ymin, dx, dy*2])

ax.plot(r_radical, radial_radical, color='gray', lw=0.5)
ax.plot(r_steinray, radial_steinray, color='gray', lw=0.5)
ax.plot(r_mc3d, radial_mc3d, color='gray', lw=0.5)
ax.plot(r_hyperion, radial_hyperion, color='black', lw=1)

ax.set_xscale('log')
ax.set_xlim(1., 1000.)
ax.xaxis.set_major_formatter(mpl.NullFormatter())

ax.set_ylim(0., 450.)
ax.yaxis.set_ticks([100., 300.])
artist = ax.text(-0.13, 0.5, r'Temperature (K)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
artists.append(artist)

ax.text(0.975, 0.95,r'$\tau_{V}=100$, $\theta=2.5^\circ$',ha='right',va='top',transform=ax.transAxes, size='small')

# RADIAL DIFFERENCE

ymin = ymargin

ax = fig.add_axes([xmin, ymin, dx, dy])

radial_steinray = interp1d_fast_loglog(r_steinray, radial_steinray, r_radical, bounds_error=False)
radial_mc3d = interp1d_fast_loglog(r_mc3d, radial_mc3d, r_radical, bounds_error=False)
radial_hyperion = interp1d_fast_loglog(r_hyperion, radial_hyperion, r_radical, bounds_error=False)

ax.plot(r_radical, (radial_steinray-radial_radical)/radial_radical*100., color='gray', lw=0.5)
ax.plot(r_radical, (radial_mc3d- radial_radical)/radial_radical*100., color='gray', lw=0.5)
ax.plot(r_radical, (radial_hyperion-radial_radical)/radial_radical*100., color='black', lw=1.0)

ax.set_xscale('log')
ax.set_xlim(1., 1000.)
ax.set_xlabel('Radius (AU)')
ax.xaxis.set_major_formatter(mpl.FixedFormatter(['1','10','100','1000']))

ax.set_ylim(-20., 20.)
ax.yaxis.set_ticks([-10., 0., 10.])
artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
artists.append(artist)

# VERITCAL ABSOLUTE

xmin = 0.5 + xmargin
ymin = ymargin + dy

ax = fig.add_axes([xmin, ymin, dx, dy*2])

ax.plot(t_radical, vertical_radical, color='gray',lw=0.5)
ax.plot(t_steinray, vertical_steinray, color='gray',lw=0.5)
ax.plot(t_mc3d, vertical_mc3d, color='gray',lw=0.5)
ax.plot(t_hyperion, vertical_hyperion, color='black',lw=1.0)

ax.set_xlim(-40., 40.)
ax.xaxis.set_ticks([])

ax.set_ylim(160., 290.)
ax.yaxis.set_ticks([180., 220., 260.])

artist = ax.text(-0.13, 0.5, r'Temperature (K)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
artists.append(artist)

ax.text(0.975, 0.95,r'$\tau_{V}=100$, $r=2$ AU',ha='right',va='top',transform=ax.transAxes, size='small')

# VERTICAL DIFFERENCE

ymin = ymargin

ax = fig.add_axes([xmin, ymin, dx, dy])

vertical_steinray = interp1d_fast(t_steinray, vertical_steinray, t_radical, bounds_error=False)
vertical_mc3d = interp1d_fast(t_mc3d, vertical_mc3d, t_radical, bounds_error=False)
vertical_hyperion = interp1d_fast(t_hyperion, vertical_hyperion, t_radical, bounds_error=False)

ax.plot(t_radical, (vertical_steinray-vertical_radical)/vertical_radical*100., color='gray',lw=0.5)
ax.plot(t_radical, (vertical_mc3d- vertical_radical)/vertical_radical*100., color='gray',lw=0.5)
ax.plot(t_radical, (vertical_hyperion-vertical_radical)/vertical_radical*100., color='black',lw=1.0)

ax.set_xlim(-40., 40.)
ax.xaxis.set_ticks([-40., -20., 0., 20., 40.])
ax.set_xlabel(r'$\theta$ (degrees)')

ax.set_ylim(-20., 20.)
ax.yaxis.set_ticks([-10., 0., 10.])

artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
artists.append(artist)

fig.savefig('%s/temperatures.eps' % output, bbox_inches='tight', bbox_extra_artists=artists)
