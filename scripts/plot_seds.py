import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as mpl

import numpy as np

from hyperion.model import AnalyticalYSOModel
from hyperion.util.constants import rsun, pi, c
from hyperion.util.integrate import interp1d_log10
from hyperion.util.functions import B_nu

prefix = 'sph_0.8.4'

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

xmargin = 0.005
ymargin = 0.005

dx = 0.5 - 2 * xmargin
dy = (0.5 - 2 * ymargin) / 6.

# Function to retrieve SEDs

def get_sed(filename, inclination=0):

    f = file(filename)
    if 'RADICAL' in filename:
        n_wav = int(f.readline())
        n_seds = int(f.readline())
    elif 'MC3D' in filename:
        n_wav = 61
        n_seds = 3
        f.readline()
        f.readline()
    elif 'MCTRANSF' in filename or 'RADMC' in filename or 'STEINRAY' in filename:
        f.readline()
        n_wav = int(f.readline())
        n_seds = int(f.readline())

    seds = []
    for ii in range(n_seds):
        if 'MC3D' in filename:
            f.readline()
            f.readline()
            f.readline()
        wav = []
        sed = []
        for jj in range(n_wav):
            if 'MC3D' in filename or 'STEINRAY' in filename:
                w, flux = f.readline().split()
            else:
                w, incl, flux = f.readline().split()
            wav.append(float(w))
            sed.append(float(flux.replace('D','E')))
        wav = np.array(wav)
        seds.append(np.array(sed))

    if 'RADICAL' in filename:
        sed = seds[inclination] / (4.*pi*rsun**2)
    elif 'MC3D' in filename:
        sed = interp1d_log10(wav, seds[inclination]*wav*10./rsun**2)
    elif 'MCTRANS' in filename:
        sed = interp1d_log10(wav, seds[inclination]*wav*1000.)
    elif 'RADMC' in filename:
        sed = interp1d_log10(wav, seds[inclination] / (4.*pi*rsun**2))
    elif 'STEINRAY' in filename:
        sed = interp1d_log10(wav, seds[inclination]*1000.*pi)

    return wav, sed

radical = ['01tau', '1tau', '10tau', '100tau']

fig = mpl.figure(figsize=(6.5,7.5))
artists = []

for i, disk_mass in enumerate([1.1e-7, 1.1e-6, 1.1e-5, 1.1e-4]):

    if i in [0,2]:
        x0 = 0.
    else:
        x0 = 0.5

    if i in [2,3]:
        y0 = 0.
    else:
        y0 = 0.5

    xmin = x0 + xmargin
    ymin = y0 + ymargin + dy * 3.

    ax2 = fig.add_axes([xmin, ymin, dx, 3*dy])

    for j in range(3):

        xmin = x0 + xmargin
        ymin = y0 + ymargin + dy * (2-j)

        ax = fig.add_axes([xmin, ymin, dx, dy])

        # Get Hyperion SED
        m = AnalyticalYSOModel(name='%s/models/pascucci_%7.1e' % (prefix,disk_mass))
        wav_hyperion, sed_hyperion = m.get_sed(inclination=j, distance=rsun)
        sed_hyperion = sed_hyperion[0]

        # Get all other SEDs
        wav_radical, sed_radical = get_sed('paper_results/RADICAL/%s/allseds.dat' % radical[i], inclination=j)
        wav_mc3d, sed_mc3d = get_sed('paper_results/MC3D/%s/sp_ray_new' % radical[i], inclination=j)
        wav_mctrans, sed_mctrans = get_sed('paper_results/MCTRANSF/%s/sp' % radical[i], inclination=j)
        wav_radmc, sed_radmc = get_sed('paper_results/RADMC/%s/sp' % radical[i], inclination=j)
        wav_steinray, sed_steinray = get_sed('paper_results/STEINRAY/%s/sp' % radical[i], inclination=j)

        # Plot differences
        ax.plot(wav_radical, (sed_mc3d(wav_radical)-sed_radical)/sed_radical*100., color='gray', lw=0.5)
        ax.plot(wav_radical, (sed_mctrans(wav_radical)-sed_radical)/sed_radical*100., color='gray', lw=0.5)#, ls='dashdot')
        ax.plot(wav_radical, (sed_radmc(wav_radical)-sed_radical)/sed_radical*100., color='gray', lw=0.5)#, ls='dotted')
        ax.plot(wav_radical, (sed_steinray(wav_radical)-sed_radical)/sed_radical*100., color='gray', lw=0.5)#, ls='dashed')
        ax.plot(wav_radical, (sed_hyperion-sed_radical)/sed_radical*100., color='black', lw=1.)

        # X-axis
        ax.set_xscale('log')
        ax.set_xlim(0.12, 2000.)

        if j == 2 and i in [2,3]:
            ax.xaxis.set_major_formatter(mpl.FixedFormatter(['0.1','1','10','100','1000','10000']))
            ax.set_xlabel(r'$\lambda$ [$\mu$m]')
        else:
            ax.xaxis.set_major_formatter(mpl.FixedFormatter([''] * 6))

        # Y-axis
        ax.set_ylim(-20., 20.)
        ax.yaxis.set_ticks([-10., 0., 10.])

        if i % 2 == 0:
            pass
        else:
            ax.yaxis.set_major_formatter(mpl.NullFormatter())

        if j == 1 and i%2 == 0:
            artist = ax.text(-0.13, 0.5, r'Difference (\%)', rotation='vertical', ha='center', va='center', transform=ax.transAxes, size='x-small')
            artists.append(artist)

        # Plot SEDs
        ax2.scatter(wav_radical, sed_radical, color='gray', marker='o', lw=0, s=5, edgecolor='none')
        ax2.loglog(wav_radical, sed_hyperion, color='black', marker='-', lw=0.5)

    # Plot stellar photosphere
    nu_radical = c/(wav_radical*1.e-4)
    ax2.loglog(wav_radical, pi*B_nu(nu_radical, 5800.)*nu_radical, ls='dashed', lw=0.5, color='black')

    # X-axis
    ax2.set_xlim(0.12, 2000.)
    ax2.xaxis.set_major_formatter(mpl.NullFormatter())
    if i%2 == 0:
        artist = ax2.text(-0.13, 0.5, r'$\lambda F_\lambda$ (ergs/cm$^2$/s)', rotation='vertical', ha='center', va='center', transform=ax2.transAxes, size='x-small')
        artists.append(artist)

    # Y-axis
    ax2.set_ylim(5.e4, 2.e11)
    if i % 2 == 0:
        pass
    else:
        ax2.yaxis.set_major_formatter(mpl.NullFormatter())
    ax2.text(0.975, 0.95, r'$\tau_{V}=%g$' % (10.**(i-1)), ha='right', va='top', transform = ax2.transAxes, size='small')

# Save plot
fig.savefig('plots/seds.eps', bbox_inches='tight', bbox_extra_artists=artists)
