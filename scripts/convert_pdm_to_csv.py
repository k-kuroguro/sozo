"""
This script converts the 3D facial landmarks in an OpenFace Point Distribution Model (PDM)
into a 3x3 matrix format CSV with inverted z-axis.

PDM format:
    [x1, x2, ..., x68, y1, y2, ..., y68, z1, z2, ..., z68]
Matrix format:
    [x1, y1, z1],
    [x2, y2, z2],
    [x3, y3, z3],
    ...
    [x68, y68, z68]

"""

import argparse
import os

import numpy as np

LANDMARK_NUM = 68
ROW_NUM = LANDMARK_NUM * 3  # 68 landmarks * 3 (x, y, z)
SKIP_ROWS = 4  # landmarks start from the 5th row


def convert_pdm_to_csv(input_file, output_file):
    pdm = np.loadtxt(input_file, skiprows=SKIP_ROWS, max_rows=ROW_NUM)
    pdm = pdm.reshape((3, -1)).T
    pdm[:, 2] *= -1  # invert z-axis

    np.savetxt(
        output_file,
        pdm,
        delimiter=",",
        header=f"Converted from {os.path.basename(input_file)}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, required=True, dest="in_file")
    parser.add_argument("-o", type=str, required=True, dest="out_file")

    args = parser.parse_args()

    convert_pdm_to_csv(args.in_file, args.out_file)
