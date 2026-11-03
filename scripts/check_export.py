#!/usr/bin/env python3
"""Check page order, A4 size, preserved proportions, and image placement."""

from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from pypdf import PdfReader
from pypdf.generic import ContentStream
from reportlab.lib.pagesizes import A4

from images_to_pdf import export_pdf


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        sizes = [(120, 360), (400, 100)]
        paths = [root / "portrait.png", root / "landscape.png"]
        for path, size in zip(paths, sizes):
            Image.new("RGB", size, "white").save(path)
        output = export_pdf(paths, root / "nested/check.pdf")
        reader = PdfReader(output)
        assert len(reader.pages) == 2
        for page, size in zip(reader.pages, sizes):
            assert abs(float(page.mediabox.width) - A4[0]) < 0.01
            assert abs(float(page.mediabox.height) - A4[1]) < 0.01
            objects = list(page["/Resources"]["/XObject"].values())
            assert len(objects) == 1
            image = objects[0].get_object()
            assert (image["/Width"], image["/Height"]) == size
            matrices = [values for values, op in ContentStream(page.get_contents(), reader).operations
                        if op == b"cm"]
            w, _, _, h, x, y = map(float, matrices[-1])
            assert x >= -0.01 and y >= -0.01
            assert x + w <= A4[0] + 0.01 and y + h <= A4[1] + 0.01
            assert abs(w / h - size[0] / size[1]) < 0.0001
        try:
            export_pdf(paths, paths[0])
        except ValueError:
            pass
        else:
            raise AssertionError("A source image must not be overwritten as a PDF")
        with Image.open(paths[0]) as original:
            assert original.size == sizes[0]
    print("OK: page order, A4, proportions, bounds, and source preservation")


if __name__ == "__main__":
    main()
