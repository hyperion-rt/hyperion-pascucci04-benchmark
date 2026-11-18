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

MASSES = ["1.1e-07", "1.1e-06", "1.1e-05", "1.1e-04"]
FORMATS = ["png", "pdf"]


wildcard_constraints:
    geometry="sph|cyl",
    mass=r"1\.1e-0[4-7]",


# The benchmark is run on a spherical polar grid. The models can also be set
# up on a cylindrical polar grid, but the temperature plot only supports the
# spherical polar grid, so the cylindrical models and SED plot are only made
# if explicitly requested, e.g. with: snakemake 0.9.12/cyl/plots/seds.png
rule all:
    input:
        expand(
            PLOTS + "/{plot}.{ext}",
            geometry="sph",
            plot=["seds", "temperatures"],
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
        "scripts/setup_{wildcards.geometry}.py"


rule run_hyperion:
    input:
        RUN + "/models/pascucci_{mass}.rtin",
    output:
        RUN + "/models/pascucci_{mass}.rtout",
    log:
        RUN + "/models/pascucci_{mass}.log",
    threads: MPI_PROCESSES
    resources:
        mpi_jobs=1,
    shell:
        "mpirun -n {threads} hyperion_{wildcards.geometry}_mpi {input} {output} > {log} 2>&1"


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


# The temperature plot only uses the most optically thick model
rule plot_temperatures:
    input:
        LABEL + "/sph/models/pascucci_1.1e-04.rtout",
    output:
        expand(LABEL + "/sph/plots/temperatures.{ext}", ext=FORMATS),
    params:
        run=LABEL + "/sph",
        plots=LABEL + "/sph/plots",
    shell:
        "python scripts/plot_temperatures.py {params.run} {params.plots}"
