configfile: "config.yaml"

PROFILE = config.get("profile", "full")

if PROFILE not in config["profiles"]:
    raise ValueError(
        "Unknown profile '{0}', should be one of: {1}".format(
            PROFILE, ", ".join(config["profiles"])
        )
    )

SETTINGS = config["profiles"][PROFILE]

# All the output for the full profile goes in a directory named after the
# version, e.g. 0.9.12, and the output for any other profile goes in e.g.
# 0.9.12_fast, so that reduced runs can never be mistaken for (or overwrite)
# the real benchmark results. Inside this there is one directory for each
# grid geometry, containing the models and the plots.
LABEL = str(config["version"])
if PROFILE != "full":
    LABEL += "_" + PROFILE

# Number of MPI processes for each Hyperion run, which can be set to "all" to
# use all the cores that Snakemake has been given with --cores
MPI_PROCESSES = config.get("mpi_processes", "all")
if MPI_PROCESSES == "all":
    MPI_PROCESSES = workflow.cores
else:
    MPI_PROCESSES = int(MPI_PROCESSES)

RUN = LABEL + "/{geometry}"
PLOTS = RUN + "/plots"

GEOMETRIES = ["sph", "cyl"]
MASSES = ["1.1e-07", "1.1e-06", "1.1e-05", "1.1e-04"]
FORMATS = ["png", "pdf"]


wildcard_constraints:
    geometry="sph|cyl",
    kind="models|models_binned",
    mass=r"1\.1e-0[4-7]",


rule all:
    input:
        expand(
            PLOTS + "/{plot}.{ext}",
            geometry=GEOMETRIES,
            plot=["seds", "seds_binned", "temperatures"],
            ext=FORMATS,
        ),


rule setup_model:
    input:
        dust="dust/pascucci_dust_isotropic.hdf5",
        wavelengths="paper_results/wavelengths.txt",
    output:
        RUN + "/models/pascucci_{mass}.rtin",
    params:
        settings=SETTINGS,
    script:
        "scripts/setup_model.py"


# The SEDs are also computed in the normal (non-monochromatic) mode for each
# model, re-using the temperatures from the model
rule setup_sed_binned:
    input:
        model=RUN + "/models/pascucci_{mass}.rtout",
        wavelengths="paper_results/wavelengths.txt",
    output:
        RUN + "/models_binned/pascucci_{mass}.rtin",
    params:
        settings=SETTINGS["binned"],
    script:
        "scripts/setup_sed_binned.py"


# Hyperion is run from the directory containing the input file, since the
# output file links to the input file using the path given on the command
# line, and the link then works from any directory
rule run_hyperion:
    input:
        RUN + "/{kind}/pascucci_{mass}.rtin",
    output:
        RUN + "/{kind}/pascucci_{mass}.rtout",
    log:
        RUN + "/{kind}/pascucci_{mass}.log",
    threads: MPI_PROCESSES
    resources:
        mpi_jobs=1,
    shell:
        "cd $(dirname {input}) && "
        "mpirun -n {threads} hyperion_{wildcards.geometry}_mpi "
        "$(basename {input}) $(basename {output}) > $(basename {log}) 2>&1"


rule plot_seds:
    input:
        expand(RUN + "/models/pascucci_{mass}.rtout", mass=MASSES, allow_missing=True),
    output:
        expand(PLOTS + "/seds.{ext}", ext=FORMATS, allow_missing=True),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_seds.py {params.run} {params.plots}"


rule plot_seds_binned:
    input:
        expand(RUN + "/models_binned/pascucci_{mass}.rtout", mass=MASSES, allow_missing=True),
    output:
        expand(PLOTS + "/seds_binned.{ext}", ext=FORMATS, allow_missing=True),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_seds.py {params.run} {params.plots} models_binned"


# The temperature plot only uses the most optically thick model
rule plot_temperatures:
    input:
        RUN + "/models/pascucci_1.1e-04.rtout",
    output:
        expand(PLOTS + "/temperatures.{ext}", ext=FORMATS, allow_missing=True),
    params:
        run=RUN,
        plots=PLOTS,
    shell:
        "python scripts/plot_temperatures.py {params.run} {params.plots}"
