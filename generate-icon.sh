#!/bin/bash
# Script to convert icon.svg to icon.png using ImageMagick or Inkscape
# This creates a 256x256 PNG suitable for Unraid and other container platforms

if command -v convert &> /dev/null; then
    echo "Using ImageMagick to convert icon..."
    convert -background none -resize 256x256 static/icon.svg static/icon.png
    echo "Created static/icon.png (256x256)"
elif command -v inkscape &> /dev/null; then
    echo "Using Inkscape to convert icon..."
    inkscape static/icon.svg --export-type=png --export-width=256 --export-height=256 --export-filename=static/icon.png
    echo "Created static/icon.png (256x256)"
elif command -v rsvg-convert &> /dev/null; then
    echo "Using rsvg-convert to convert icon..."
    rsvg-convert -w 256 -h 256 static/icon.svg -o static/icon.png
    echo "Created static/icon.png (256x256)"
else
    echo "Error: No suitable converter found. Please install one of:"
    echo "  - ImageMagick: brew install imagemagick"
    echo "  - Inkscape: brew install inkscape"
    echo "  - librsvg: brew install librsvg"
    exit 1
fi

echo "Done! You can now use static/icon.png for Unraid and other platforms."
