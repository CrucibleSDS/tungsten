import logging
import typing
from typing import IO, Optional

import cv2
import numpy as np
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import (
    LITERALS_ASCII85_DECODE,
    LITERALS_ASCIIHEX_DECODE,
    LITERALS_CCITTFAX_DECODE,
    LITERALS_DCT_DECODE,
    LITERALS_FLATE_DECODE,
    LITERALS_JBIG2_DECODE,
    LITERALS_JPX_DECODE,
    LITERALS_LZW_DECODE,
    LITERALS_RUNLENGTH_DECODE,
    PDFObjRef,
    PDFStream
)
from pdfminer.psparser import PSLiteralTable
from PIL import Image

from tungsten.parsers.sds_parser import SdsParserInjector
from tungsten.pictograms.pictograms import Pictogram, get_pictograms_cv2

PillowMode = typing.Literal[
    "1", "CMYK", "F", "HSV", "I", "L", "LAB", "P", "RGB", "RGBA", "RGBX", "YCbCr"]


class SigmaAldrichPictogramInjector(SdsParserInjector):
    logger: logging.Logger
    pictograms: dict[Pictogram, np.ndarray]

    def __init__(self):
        self.logger = logging.getLogger(f"tungsten:{self.__class__.__name__}")
        self.pictograms = get_pictograms_cv2()
        self.pictograms_scaled = {k: cv2.resize(v, (150, 150)) for k, v in self.pictograms.items()}

    def generate_injections(self, io: IO[bytes]) -> list[dict]:
        self.logger.info("Received request to generate pictogram injections")
        images = self._extract_images(io)

        matches = set()
        for image in images:
            if 0.8 < image.shape[0] / image.shape[1] < 1.2:
                match = self._match(image)
                # Image.fromarray(
                #     cv2.putText(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), str(match.value)[11:],
                #                 (0, 140), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)).show()
                matches.add(match)
        return [{"pictograms": [match.value for match in matches]}]

    def _match(self, image: np.ndarray) -> Optional[Pictogram]:
        """Return pictogram enum match of image if it exceeds the confidence threshold"""
        CONFIDENCE_THRESHOLD = 0.9

        # Create features for test image
        scaled = cv2.resize(image, (150, 150))

        similarities: dict[Pictogram, float] = {}
        pict_keys = self.pictograms.keys()
        for pict_key in pict_keys:
            result = cv2.matchTemplate(scaled, self.pictograms_scaled[pict_key],
                                       cv2.TM_CCORR_NORMED)
            max_val = cv2.minMaxLoc(result)[1]
            similarities[pict_key] = max_val
        self.logger.debug(
            f"Confidence levels (CONFIDENCE_THRESHOLD {CONFIDENCE_THRESHOLD}): {similarities}")
        confident = {k: v for k, v in similarities.items() if v > CONFIDENCE_THRESHOLD}

        if not len(confident):
            return None

        choice = max(confident, key=lambda k: confident[k])
        self.logger.info(f"Chose {choice.value}")

        return choice

    def _extract_images(self, io: IO[bytes]) -> list[np.ndarray]:
        """Returns a list of BGR OpenCV images from PDF"""
        # Because the pdfminer.six[image] utilities of images are inadequate
        # There needs to be a custom loading mechanism for PDF images
        self.logger.debug("Importing images...")

        # Create relevant pdfminer tools
        # noinspection PyTypeChecker
        parser = PDFParser(io)
        document = PDFDocument(parser)
        resource_manager = PDFResourceManager()
        device = PDFPageAggregator(resource_manager)
        interpreter = PDFPageInterpreter(resource_manager, device)

        images = []

        # Need to grab XObjects from each page to find all image embeddings
        for i, page in enumerate(PDFPage.create_pages(document)):
            self.logger.debug(f"Getting images from page {i + 1}...")
            interpreter.process_page(page)

            # Get XObject resource for page
            x_object = typing.cast(dict, page.resources.get("XObject"))
            if not x_object:
                continue
            for obj_name in x_object.keys():
                # Get all PDFObjRefs in the XObject (could possibly be a PDFStream for an image)
                obj_ref = x_object[obj_name]
                if not isinstance(obj_ref, PDFObjRef):
                    continue
                # Get the object that it is referencing
                obj = document.getobj(obj_ref.objid)
                # Check if the referenced object is a PDFStream for an Image
                if not isinstance(obj, PDFStream) or obj.get_any(
                        ("Subtype",)) != PSLiteralTable.intern("Image"):
                    continue
                # Retrieve raw image byte data
                raw_data = obj.get_data()

                # Retrieve metadata necessary to load image
                width = obj.get_any(("W", "Width"))
                height = obj.get_any(("H", "Height"))
                bits = obj.get_any(("BPC", "BitsPerComponent"), 1)
                channels = len(raw_data) / width / height / (bits / 8)

                # Detect if image uses indexed color
                palette = None
                color_space = obj.get_any(("ColorSpace",))
                if color_space and PSLiteralTable.intern("Indexed") in color_space:
                    # If indexed, the image data itself is not enough to load the image properly
                    # There needs to be a palette loaded
                    # The palette is another PDFStream byte stream referenced by PDFObjRef
                    palette_obj_ref = next(
                        (e for e in color_space if isinstance(e, PDFObjRef)), None)
                    assert palette_obj_ref
                    # Load the palette
                    palette_stream = document.getobj(palette_obj_ref.objid)
                    assert isinstance(palette_stream, PDFStream)
                    palette = palette_stream.get_data()

                # Depending on the number of bits and channels, Pillow/PIL byte image loader modes
                mode: PillowMode
                match (bits, channels):
                    case (1, _):
                        mode = "1"
                    case (8, 1):
                        # 8-Bit pixel encoding are either grayscale (L) or indexed (P)
                        if not palette:
                            mode = "L"
                        else:
                            mode = "P"
                    case (8, 3):
                        mode = "RGB"
                    case (8, 4):
                        mode = "CMYK"
                    case _:
                        raise NotImplementedError(
                            f"Mode for {bits} bits and {channels} channels is not implemented.")

                image_pil: Image
                # Get the type of PDF image filter https://en.wikipedia.org/wiki/PDF#Raster_images
                filters = obj.get_filters()
                assert len(filters) == 1
                filter = filters[0][0]
                # Process image filter
                self.logger.debug(f"Reading image in mode {mode} with filter {filter}...")
                if filter in LITERALS_FLATE_DECODE:
                    image_pil = Image.frombytes(
                        mode=mode,
                        size=(width, height),
                        data=raw_data,
                        decoder_name="raw"
                    )
                elif filter in tuple(x for y in [LITERALS_LZW_DECODE,
                                                 LITERALS_ASCII85_DECODE,
                                                 LITERALS_ASCIIHEX_DECODE,
                                                 LITERALS_RUNLENGTH_DECODE,
                                                 LITERALS_CCITTFAX_DECODE,
                                                 LITERALS_DCT_DECODE,
                                                 LITERALS_JBIG2_DECODE,
                                                 LITERALS_JPX_DECODE] for x in y):
                    raise NotImplementedError(
                        "Only supports FlateDecode (zlib) image filter for now")
                else:
                    raise ValueError("Invalid PDF Image Filter")

                # If image was loaded in 8-bit palette mode, apply the palette
                if mode == "P" and palette:
                    image_pil.putpalette(palette)

                # Convert Pillow/PIL image to OpenCV image
                # noinspection PyTypeChecker
                image_arr = np.asarray(image_pil.convert("RGB"))
                image_cv2 = cv2.cvtColor(image_arr, cv2.COLOR_RGB2BGR)
                if image_cv2 is not None:
                    images.append(image_cv2)

        return images
