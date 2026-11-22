"""Test du parseur JPEG sans matériel : python -m unittest discover -s tests"""
import os
import sys
import unittest

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))
from serial_receiver import JpegStreamParser, decode_jpeg  # noqa: E402


def make_jpeg(value):
    img = np.full((24, 32, 3), value, dtype=np.uint8)
    return cv2.imencode(".jpg", img)[1].tobytes()


class ParserTest(unittest.TestCase):
    def test_images_coupees_et_bruit(self):
        a, b = make_jpeg(40), make_jpeg(200)
        stream = b"bruit" + a + b"xx" + b
        parser, out = JpegStreamParser(), []
        for i in range(0, len(stream), 7):         # morceaux de 7 octets
            out += parser.feed(stream[i:i + 7])
        self.assertEqual(out, [a, b])
        self.assertIsNotNone(decode_jpeg(out[0]))

    def test_image_incomplete_non_emise(self):
        a = make_jpeg(90)
        self.assertEqual(JpegStreamParser().feed(a[:-3]), [])


if __name__ == "__main__":
    unittest.main()
