from typing import cast

import cv2
import numpy as np

from .schemas import FacialLandmarks2d, FacialLandmarks3d, HeadPose


class HeadPoseEstimator:
    """Head pose estimator by solving PnP problem."""

    def __init__(self, landmarks_3d_file_path: str):
        """
        Args:
            landmarks_3d_file_path (str): Path to the file containing the 3D facial landmarks, which is the output of `scripts/convert_pdm_to_csv.py`.
        """

        self._landmarks_3d = FacialLandmarks3d(np.loadtxt(landmarks_3d_file_path, delimiter=","))

        self._focal_length: int | None = None
        self._camera_center: tuple[float, float] | None = None
        self._camera_matrix: np.ndarray | None = None

        self._dist_coeefs = np.zeros((4, 1))
        self._r_vec: np.ndarray | None = None
        self._t_vec: np.ndarray | None = None

    def is_image_size_set(self) -> bool:
        return (
            self._focal_length is not None
            and self._camera_center is not None
            and self._camera_matrix is not None
        )

    def set_image_size(self, image_height: int, image_width: int):
        """Set image size to calculate focal length, camera center and camera matrix."""
        self._focal_length = image_width
        self._camera_center = (image_width / 2, image_height / 2)
        self._camera_matrix = np.array(
            [
                [self._focal_length, 0, self._camera_center[0]],
                [0, self._focal_length, self._camera_center[1]],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

    def estimate(self, landmarks_2d: FacialLandmarks2d) -> HeadPose:
        """Estimate head pose from 2D facial landmarks.

        This method requires the image size to be set first using `set_image_size`.

        Args:
            landmarks_2d (FacialLandmarks2d): 2D facial landmarks.

        Returns:
            HeadPose: Estimated head pose.

        Raises:
            RuntimeError: If image size is not set.
        """
        if not self.is_image_size_set():
            raise RuntimeError("Image size is not set. Call set_image_size method first.")

        self._camera_matrix = cast(
            np.ndarray, self._camera_matrix
        )  # is_image_size_set() guarantees that _camera_matrix is not None

        self._r_vec, self._t_vec = self._solve_pose(
            self._landmarks_3d,
            landmarks_2d,
            self._r_vec,
            self._t_vec,
            self._camera_matrix,
            self._dist_coeefs,
        )

        r_mat, _ = cv2.Rodrigues(self._r_vec)
        *_, euler_angles = cv2.decomposeProjectionMatrix(np.hstack((r_mat, self._t_vec)))
        return HeadPose(
            float(euler_angles[1][0]), float(euler_angles[0][0]), float(euler_angles[2][0])
        )

    @staticmethod
    def _solve_pose(
        landmarks_3d: FacialLandmarks3d,
        landmarks_2d: FacialLandmarks2d,
        r_vec: np.ndarray | None,
        t_vec: np.ndarray | None,
        camera_matrix: np.ndarray,
        dist_coeefs: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        landmarks_3d_f32 = landmarks_3d.astype(np.float32)
        landmarks_2d_f32 = landmarks_2d.astype(np.float32)

        if r_vec is None or t_vec is None:
            _, new_r_vec, new_t_vec = cv2.solvePnP(
                landmarks_3d_f32, landmarks_2d_f32, camera_matrix, dist_coeefs
            )
        else:
            _, new_r_vec, new_t_vec = cv2.solvePnP(
                landmarks_3d_f32,
                landmarks_2d_f32,
                camera_matrix,
                dist_coeefs,
                rvec=r_vec,
                tvec=t_vec,
                useExtrinsicGuess=True,
            )
        return new_r_vec, new_t_vec
