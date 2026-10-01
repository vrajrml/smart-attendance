import json
from pathlib import Path

import cv2
import numpy as np


# Project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]

# Face recognition model paths.
DETECTOR_MODEL = (
    BASE_DIR
    / "models"
    / "face_detection_yunet_2023mar.onnx"
)

RECOGNIZER_MODEL = (
    BASE_DIR
    / "models"
    / "face_recognition_sface_2021dec.onnx"
)


class FaceRecognitionService:
    """Service for detecting faces and generating face embeddings."""

    def __init__(self):
        """Load the YuNet detector and SFace recognizer."""

        if not DETECTOR_MODEL.exists():
            raise FileNotFoundError(
                f"Face detector model not found: {DETECTOR_MODEL}"
            )

        if not RECOGNIZER_MODEL.exists():
            raise FileNotFoundError(
                f"Face recognition model not found: {RECOGNIZER_MODEL}"
            )

        self.detector = cv2.FaceDetectorYN.create(
            str(DETECTOR_MODEL),
            "",
            (320, 320),
            0.6,
            0.3,
            5000
        )

        self.recognizer = cv2.FaceRecognizerSF.create(
            str(RECOGNIZER_MODEL),
            ""
        )

    def detect_faces(self, image):
        """
        Detect faces in an image.

        Returns:
            List of detected face arrays.
        """

        if image is None:
            return []

        height, width = image.shape[:2]

        self.detector.setInputSize(
            (width, height)
        )

        _, faces = self.detector.detect(image)

        if faces is None:
            return []

        return list(faces)

    def extract_face(self, image, face):
        """
        Align and crop a detected face for recognition.
        """

        return self.recognizer.alignCrop(
            image,
            face
        )

    def generate_embedding(self, image, face):
        """
        Generate an SFace embedding.

        Returns:
            JSON string containing the embedding.
        """

        aligned_face = self.extract_face(
            image,
            face
        )

        feature = self.recognizer.feature(
            aligned_face
        )

        feature = np.asarray(
            feature,
            dtype=np.float32
        ).flatten()

        return json.dumps(
            feature.tolist()
        )

    @staticmethod
    def embedding_to_numpy(encoding):
        """
        Convert a stored JSON encoding into NumPy format.
        """

        if isinstance(encoding, str):
            values = json.loads(encoding)
        else:
            values = encoding

        return np.asarray(
            values,
            dtype=np.float32
        )

    def compare_embeddings(
        self,
        stored_encoding,
        new_embedding
    ):
        """
        Compare two face embeddings using cosine similarity.

        Returns:
            Float similarity score between the embeddings.
        """

        stored = self.embedding_to_numpy(
            stored_encoding
        )

        new = self.embedding_to_numpy(
            new_embedding
        )

        score = self.recognizer.match(
            stored.reshape(1, -1),
            new.reshape(1, -1),
            cv2.FaceRecognizerSF_FR_COSINE
        )

        return float(score)


face_service = FaceRecognitionService()
