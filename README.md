# SCENIC Pipeline Runner

This repository provides a SLURM-submittable wrapper for running the [SCENIC](https://github.com/aertslab/SCENICprotocol) workflow for single-cell regulatory network inference. It includes conversion scripts, configuration templates, and a pipeline launcher using Nextflow and Singularity.

---

## Repository Structure

* `pipeline_runner.py` — Python wrapper to launch SCENIC via Nextflow using `config.yaml`
* `h5ad2loom.py` — Utility script to convert `.h5ad` files to `.loom` format
* `config.yaml` — Central configuration file specifying paths for inputs/outputs and parameters
* `nextflow.config` — Executor settings (e.g., SLURM setup and container use)
* `slurm_submit.sh` — Submission script for launching the pipeline on a SLURM cluster
* `environment.yaml` — Conda environment file for running the Python wrapper and conversion scripts

---

## Requirements

* Python ≥ 3.8
* [Conda](https://docs.conda.io/en/latest/)
* [Nextflow](https://www.nextflow.io/) (DSL1 enabled)
* [Singularity](https://sylabs.io/singularity/)
* SLURM-compatible HPC environment

---

## Environment Setup

Use `conda` to install the required Python dependencies (used for the helper scripts):

```bash
conda env create -f environment.yaml
conda activate scenic
```

---

## Usage

### 1. Convert `.h5ad` to `.loom`

```bash
python h5ad2loom.py -i ./data/input.h5ad -o ./data/output.loom
```

### 2. Configure the pipeline

Edit `config.yaml` to specify:

* Input `.loom` file
* Output file path
* Paths to transcription factors, motif databases, and ranking DBs
* SCENIC thresholds

### 3. Run the pipeline

```bash
chmod +x slurm_submit.sh
./slurm_submit.sh
```

---

## Output

* Final `.loom` object with inferred GRNs
* Intermediate results in results directory
* Execution metadata:

  * `trace.txt`
  * `report.html`
  * `timeline.html`
  * DAG graph
