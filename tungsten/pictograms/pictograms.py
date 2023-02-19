from enum import Enum
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


class Pictogram(Enum):
    PICT_GHS01_EXPLOSIVE = "PICT_GHS01_EXPLOSIVE"
    PICT_GHS02_FLAMMABLE = "PICT_GHS02_FLAMMABLE"
    PICT_GHS03_OXIDIZING = "PICT_GHS03_OXIDIZING"
    PICT_GHS04_COMPRESSED_GAS = "PICT_GHS04_COMPRESSED_GAS"
    PICT_GHS05_CORROSIVE = "PICT_GHS05_CORROSIVE"
    PICT_GHS06_TOXIC = "PICT_GHS06_TOXIC"
    PICT_GHS07_HARMFUL = "PICT_GHS07_HARMFUL"
    PICT_GHS08_HEALTH_HAZARD = "PICT_GHS08_HEALTH_HAZARD"
    PICT_GHS09_ENVIRONMENTAL_HAZARD = "PICT_GHS09_ENVIRONMENTAL_HAZARD"


# noinspection PyTypeChecker
def get_pictograms_cv2() -> dict[Pictogram, np.ndarray]:
    pictogram_dir = Path(__file__).absolute().parent
    return {
        Pictogram.PICT_GHS01_EXPLOSIVE:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "explos.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS02_FLAMMABLE:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "flamme.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS03_OXIDIZING:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "rondflam.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS04_COMPRESSED_GAS:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "bottle.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS05_CORROSIVE:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "acid_red.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS06_TOXIC:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "skull.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS07_HARMFUL:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "exclam.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS08_HEALTH_HAZARD:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "silhouete.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
        Pictogram.PICT_GHS09_ENVIRONMENTAL_HAZARD:
            cv2.cvtColor(np.asarray(
                Image.open(Path(pictogram_dir, "Aquatic-pollut-red.gif")).convert("RGB")),
                cv2.COLOR_RGB2BGR),
    }
