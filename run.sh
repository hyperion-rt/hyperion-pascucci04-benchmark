#!/bin/bash -x

VERSION=0.8.4

mpiexec -n 8 hyperion_sph_mpi sph_$VERSION/models/pascucci_1.1e-07.rt{in,out}
mpiexec -n 8 hyperion_sph_mpi sph_$VERSION/models/pascucci_1.1e-06.rt{in,out}
mpiexec -n 8 hyperion_sph_mpi sph_$VERSION/models/pascucci_1.1e-05.rt{in,out}
mpiexec -n 8 hyperion_sph_mpi sph_$VERSION/models/pascucci_1.1e-04.rt{in,out}

