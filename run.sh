#!/bin/bash -x

VERSION=0.8.10

hyperion -m 24 sph_$VERSION/models/pascucci_1.1e-07.rt{in,out}
hyperion -m 24 sph_$VERSION/models/pascucci_1.1e-06.rt{in,out}
hyperion -m 24 sph_$VERSION/models/pascucci_1.1e-05.rt{in,out}
hyperion -m 24 sph_$VERSION/models/pascucci_1.1e-04.rt{in,out}

