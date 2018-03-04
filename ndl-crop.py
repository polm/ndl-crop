#!/usr/bin/env python3
import cv2
from argh import ArghParser, arg

def get_contours(img):
    """Threshold the image and get contours."""
    # First make the image 1-bit and get contours
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the right threshold level
    tl = 100
    ret, thresh = cv2.threshold(imgray, tl, 255, 0)
    while white_percent(thresh) > 0.85:
        tl += 10
        ret, thresh = cv2.threshold(imgray, tl, 255, 0)

    # for debugging
    #cv2.imwrite('thresh.jpg', thresh)
    img2, contours, hierarchy = cv2.findContours(thresh, 1, 2)

    # filter contours that are too large or small
    size = get_size(img)
    contours = [cc for cc in contours if contourOK(cc, size)]
    return contours

def get_size(img):
    """Return the size of the image in pixels."""
    ih, iw = img.shape[:2]
    return iw * ih

def white_percent(img):
    """Return the percentage of the thresholded image that's white."""
    return cv2.countNonZero(img) / get_size(img)

def contourOK(cc, size=1000000):
    """Check if the contour is a good predictor of photo location."""
    x, y, w, h = cv2.boundingRect(cc)
    if w < 50 or h < 50: return False # too narrow or wide is bad
    area = cv2.contourArea(cc)
    return area < (size * 0.5) and area > 200

def near_edge(img, contour):
    """Check if a contour is near the edge in the given image."""
    x, y, w, h = cv2.boundingRect(contour)
    ih, iw = img.shape[:2]
    mm = 20 # margin in pixels
    return (x < mm
            or x + w > iw - mm
            or y < mm
            or y + h > ih - mm)


def get_boundaries(img, contours):
    """Find the boundaries of the photo in the image using contours."""
    # margin is the minimum distance from the edges of the image, as a fraction
    ih, iw = img.shape[:2]
    minx = iw
    miny = ih
    maxx = 0
    maxy = 0

    for cc in contours:
        if near_edge(img, cc): continue
        x, y, w, h = cv2.boundingRect(cc)
        if x < minx: minx = x
        if y < miny: miny = y
        if x + w > maxx: maxx = x + w
        if y + h > maxy: maxy = y + h

    return (minx, miny, maxx, maxy)

def crop(img, boundaries):
    """Crop the image to the given boundaries."""
    minx, miny, maxx, maxy = boundaries
    return img[miny:maxy, minx:maxx]

def autocrop_image(input_file, output_file=None):
    """Autocrop the photograph from the given image."""
    if not ofname:
        parts = fname.split('.')
        assert len(parts) > 1, "Can't automatically choose output name if there's no file extension!"
        ofname = '.'.join(parts[:-1], 'cropped', parts[-1])

    img = cv2.imread(fname)
    contours = get_contours(img)
    #cv2.drawContours(img, contours, -1, (0,255,0)) # draws contours, good for debugging
    bounds = get_boundaries(img, contours)
    cropped = crop(img, bounds)
    if get_size(cropped) < 10000: return # too small
    cv2.imwrite(ofname, cropped)

if __name__ == '__main__':
    parser = ArghParser()
    parser.set_default_command(autocrop_image)
    parser.dispatch()
