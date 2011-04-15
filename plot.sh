#!/bin/bash

rm plots/*

python scripts/plot_seds.py
python scripts/plot_temperatures.py
