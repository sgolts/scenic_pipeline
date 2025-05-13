import os
import sys
import argparse
import logging
import traceback
from pathlib import Path
import yaml
import json
import shutil
import subprocess

def run_command(command, capture_output=False, text=True):
    """
    Runs a command and streams the output to the console in real-time.

    Args:
        command (str or list): The command to run as a string or a list of arguments.
        capture_output (bool): Whether to capture the command's output. Set to False for real-time output.
        text (bool): Whether to decode the output as text.

    Returns:
        int: The return code of the command.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=text,
            shell=True,
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        return process.returncode

    except Exception as e:
        print(f"Command failed with error: {e}")
        return 1  # Return a non-zero exit code to indicate failure


def create_output_directory(config, overwrite):
    """
    Creates the output directory specified in the config.

    Args:
        config (dict): A dictionary containing configuration settings, including 'paths' and 'output_directory'.
        overwrite (bool): If True, overwrite an existing directory. If False, raise an error if the directory exists.
    """
    output_dir = config['paths']['output_directory']

    if os.path.exists(output_dir):
        if overwrite:
            try:
                shutil.rmtree(output_dir)
                logging.info(f"Overwriting existing output directory: {output_dir}")
            except Exception as e:
                logging.error(f"Failed to overwrite existing output directory: {e}")
                raise
        else:
            logging.error(f"Output directory already exists: {output_dir}")
            raise ValueError(f"Output directory '{output_dir}' already exists. Use --overwrite to replace.")

    try:
        working_dir = f"{output_dir}work/"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(working_dir, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")
        logging.info(f"Created working directory: {working_dir}")
        return working_dir
    except Exception as e:
        logging.error(f"Failed to create output directory: {e}")
        raise


def check_nextflow_available():
    """
    Checks if the 'nextflow' command is available in the system's PATH.

    Raises:
        RuntimeError: If the 'nextflow' command is not found.
    """
    try:
        subprocess.run(['nextflow', '-version'], capture_output=True, check=True)
        logging.info("Nextflow is available.")     
    except FileNotFoundError:
        raise RuntimeError("Error: The 'nextflow' command is not found. Make sure Nextflow is installed and in your PATH.")
    except subprocess.CalledProcessError:
        raise RuntimeError("Error: Nextflow command execution failed. Please verify your Nextflow installation.")


def load_yaml(filepath):
    """
    Loads a YAML file and returns its content as a Python dictionary.
    """
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None


def setup_logging():
    """Sets up logging to both console and file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to console
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SCENIC pipeline via Nextflow.")
    parser.add_argument(
        "--config_path",
        dest="config_path",
        default="./config.yaml",
        help="Path to the input configurtion file",
    )

    parser.add_argument(
        "--overwrite",
        dest="force",
        action="store_true", # Make --force a boolean flag
        help="If present, clear and overwrite existing output directory",
    )

    args = parser.parse_args()
    config_path = args.config_path
    force = args.force
    setup_logging()

    logging.info(f"Config file path: {config_path}")
    logging.info(f"Force overwrite: {force}")

    # check nextflow
    check_nextflow_available()

    """ Load the config """
    config = load_yaml(config_path)    
    for k, v_dict in config.items():
        logging.info(f"Configuration for: {k}")
        for key, value in v_dict.items():
            logging.info(f"\t {key} : {value}")

    """ Set up the directories """
    working_dir = create_output_directory(config, force)

    """ Set up pipeline paths """
    output_dir = config['paths']['output_directory']
    loom_input = config['pipeline']['loom_input']
    loom_output = config['pipeline']['loom_output']
    tfs = config['pipeline']['TFs']
    motifs = config['pipeline']['motifs']
    db = config['pipeline']['db']
    thr_min_genes = config['pipeline'].get('thr_min_genes', 1)
    thr_min_cells = config['pipeline'].get('thr_min_cells', 1)

    """ set up the nextflow command """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    process_name = f"{config['nextflow']['process_name']}_{timestamp}"

    flow_config = config['nextflow']['nextflow_config']

    nextflow_command = (
        f"nextflow run aertslab/SCENICprotocol"
        f" --loom_input {loom_input}"
        f" --loom_output {loom_output}"
        f" --TFs {tfs}"
        f" --motifs {motifs}"
        f" --db {db}"
        f" --thr_min_genes {thr_min_genes}"
        f" --thr_min_cells {thr_min_cells}"
        f" --transpose"
        f" -work-dir {working_dir}"
        f" -c {flow_config}"
        f" -resume"
        f" -name {process_name}"
        f" -ansi-log false"
        f" -with-report"
        f" -with-dag"
        f" -with-timeline"
        f" -with-trace"
        f" -profile singularity"
    )

    logging.info(f" ---------- Prepared Nextflow command: ")
    logging.info(f"{nextflow_command}")
    return_code = run_command(nextflow_command)
    
    if not return_code == 0:
        raise RuntimeError("Pipeline failed!")

    return_code = run_command("nextflow clean -f")
    logging.info(f"Nextflow clean up complete!")
    logging.info(f"Pipeline complete!")
