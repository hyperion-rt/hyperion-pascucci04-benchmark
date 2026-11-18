#!/bin/bash

VERSION="0.9.12"

if [ ! -d "plots_sph_$VERSION" ]; then
  mkdir "plots_sph_$VERSION"
else
  rm plots_sph_$VERSION/*
fi

python scripts/plot_seds.py "sph_$VERSION" "plots_sph_$VERSION"

python scripts/plot_temperatures.py "sph_$VERSION" "plots_sph_$VERSION"

