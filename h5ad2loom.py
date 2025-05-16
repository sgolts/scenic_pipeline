#!/usr/bin/env python3

import argparse
import anndata as ad
import numpy as np
import loompy as lp
import os

def convert_h5ad_to_loom(h5ad_path, loom_out_path):
    # Load AnnData object
    adata = ad.read_h5ad(h5ad_path)

    # Clean gene and cell names
    adata.var_names = adata.var_names.str.upper().str.strip()
    adata.obs_names = adata.obs_names.str.strip()

    # Convert to native strings (no b'' bytes)
    genes = np.array(adata.var_names.tolist(), dtype=str)
    cells = np.array(adata.obs_names.tolist(), dtype=str)

    # Prepare loom row and column attributes
    row_attrs = {
        "features": genes
    }
    col_attrs = {
        "CellID": cells,
        "nGene": np.array((adata.X > 0).sum(axis=1)).flatten(),
        "nUMI": np.array(adata.X.sum(axis=1)).flatten(),
    }

    # Write loom file
    print(f"Writing loom file to: {loom_out_path}")
    lp.create(loom_out_path, adata.X.T, row_attrs, col_attrs)
    print("Loom file created successfully.")

# USAGE: python convert_h5ad_to_loom.py -i my_data.h5ad -o my_data.loom
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert AnnData (.h5ad) to SCENIC-compatible loom file.")
    parser.add_argument("--input", "-i", required=True, help="Path to input h5ad file.")
    parser.add_argument("--output", "-o", required=True, help="Path to output loom file.")
    args = parser.parse_args()

    convert_h5ad_to_loom(args.input, args.output)