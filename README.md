# ndl-crop

This is a script to crop scans of old photobooks from the NDL like those linked
[here](http://dl.ndl.go.jp/ja/photo.html). It's written for Python 3 and uses
OpenCV for the heavy lifting.

## Examples

Uncropped picture on the left, post auto-crop on the right.

![Example 1](img/example1.jpg?raw=true)

![Example 2](img/example2.jpg?raw=true)

![Example 3](img/example3.jpg?raw=true)

![Example 4](img/example4.jpg?raw=true)

## Usage

Check out this repository, install the requirements, and feed it an image. It's
recommended you use a virtualenv.

    git clone https://github.com/polm/ndl-crop
    cd ndl-crop
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    wget -O test.jpg 'http://dl.ndl.go.jp/view/jpegOutput?itemId=info%3Andljp%2Fpid%2F764232&contentNo=7&outputScale=4'
    ./ndl-crop.py test.jpg
    # output is at test.cropped.jpg

If you have a folder full of images you can loop over it in bash.

    for ii in raw-images/*; do
        ./ndl-crop.py $ii || true # sometimes it might fail
    done

## How it Works

![Process GIF](img/process1.gif?raw=true)

1. Load the image
2. Threshold the image
3. Adjust the threshold until a certain percent is black
4. Generate contours
5. Remove contours that are too large, small, near the edges, etc.
6. Use the remaining contours to generate a bounding box for the crop

## Limitations

This is designed to handle scans of single photos in albums and may not work
well in the following cases.

- spreads
- single lines of text
- multiple images on one page
- scans with calibration scales in the margins
- scans where the boundary between the photo and the paper is unclear
- album covers

## Making a Process GIF

Use the `-r` flag to enable output and make a gif from that using ImageMagick.

    ./ndl-crop.py input.jpg
    mogrify -resize 600x1000 frames/*
    convert -delay 30 -loop 0 frames/* process.gif

## License

WTFPL, do as you please. 
