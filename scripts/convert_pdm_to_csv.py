import argparse
import os

import numpy as np

LANDMARK_NUM = 68
ROW_NUM = LANDMARK_NUM * 3  # 68 landmarks * 3 (x, y, z)
SKIP_ROWS = 4  # landmarks start from the 5th row


def convert_pdm_to_csv(input_file, output_file):
    """Convert the 3D facial landmarks in an OpenFace Point Distribution Model (PDM) into a 3x3 matrix format CSV with inverted z-axis."""

    pdm = np.loadtxt(input_file, skiprows=SKIP_ROWS, max_rows=ROW_NUM)
    pdm = pdm.reshape(
        (3, -1)
    ).T  # [x1, x2, ..., x68, y1, y2, ..., y68, z1, z2, ..., z68] -> [[x1, y1, z1], [x2, y2, z2], ..., [x68, y68, z68]]
    pdm[:, 2] *= -1  # invert z-axis

    np.savetxt(
        output_file,
        pdm,
        delimiter=",",
        fmt="%.10f",
        header=f"Converted from {os.path.basename(input_file)}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=convert_pdm_to_csv.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, required=True)

    args = parser.parse_args()

    convert_pdm_to_csv(args.input, args.output)
