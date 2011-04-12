#!/bin/bash
mpirun -n 8 hyperion_sph_mpi sph_0.7.6/models/pascucci_1.1e-07.rt{in,out}
mpirun -n 8 hyperion_sph_mpi sph_0.7.6/models/pascucci_1.1e-06.rt{in,out}
mpirun -n 8 hyperion_sph_mpi sph_0.7.6/models/pascucci_1.1e-05.rt{in,out}
mpirun -n 8 hyperion_sph_mpi sph_0.7.6/models/pascucci_1.1e-04.rt{in,out}

