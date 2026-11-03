#!/usr/bin/env python3
"""Combine generated page images into an A4 PDF in the given order."""

import argparse
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def export_pdf(images, output):
    paths = [Path(image) for image in images]
    output = Path(output)
    if not paths:
        raise ValueError("At least one page image is required")
    if output.suffix.lower() != ".pdf":
        raise ValueError("Output must have a .pdf extension")
    if output.resolve() in {path.resolve() for path in paths}:
        raise ValueError("Output must not overwrite a source image")
    readers = [ImageReader(str(path)) for path in paths]
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    pdf.setTitle(output.stem)
    pdf.setAuthor("")
    width, height = A4
    for image in readers:
        image_width, image_height = image.getSize()
        scale = min(width / image_width, height / image_height)
        draw_width, draw_height = image_width * scale, image_height * scale
        pdf.drawImage(image, (width - draw_width) / 2, (height - draw_height) / 2,
                      width=draw_width, height=draw_height)
        pdf.showPage()
    pdf.save()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path, help="Page images in reading order")
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args()
    print(export_pdf(args.images, args.output))


if __name__ == "__main__":
    main()
