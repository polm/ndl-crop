#!/usr/bin/env python3
import os
import cv2
from argh import ArghParser, arg

frame = 0
record = False

def write_frame(img, contours=None, rect=None):
    if not record: return
    global frame 
    frame += 1
    if contours:
        img = img.copy()
        cv2.drawContours(img, contours, -1, (0,255,0), 3)
    if rect:
        img = img.copy()
        cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (255, 255, 0), 3)
    cv2.imwrite('frames/frame{:02d}.png'.format(frame), img)

def get_contours(img):
    """Threshold the image and get contours."""
    # First make the image 1-bit and get contours
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the right threshold level
    tl = 100
    ret, thresh = cv2.threshold(imgray, tl, 255, 0)
    write_frame(thresh)
    while white_percent(thresh) > 0.85:
        tl += 10
        ret, thresh = cv2.threshold(imgray, tl, 255, 0)
        write_frame(thresh)

    contours, hierarchy = cv2.findContours(thresh, 1, 2)
    write_frame(img, contours=contours)

    # filter contours that are too large or small
    contours = [cc for cc in contours if contourOK(img, cc)]
    write_frame(img, contours=contours)
    return contours

def get_size(img):
    """Return the size of the image in pixels."""
    ih, iw = img.shape[:2]
    return iw * ih

def white_percent(img):
    """Return the percentage of the thresholded image that's white."""
    return cv2.countNonZero(img) / get_size(img)

def contourOK(img, cc):
    """Check if the contour is a good predictor of photo location."""
    if near_edge(img, cc): return False # shouldn't be near edges
    x, y, w, h = cv2.boundingRect(cc)
    if w < 100 or h < 100: return False # too narrow or wide is bad
    area = cv2.contourArea(cc)
    if area < (get_size(img) * 0.3): return False
    if area < 200: return False
    return True

def near_edge(img, contour):
    """Check if a contour is near the edge in the given image."""
    x, y, w, h = cv2.boundingRect(contour)
    ih, iw = img.shape[:2]
    mm = 0 # margin in pixels
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
        x, y, w, h = cv2.boundingRect(cc)
        if x < minx: minx = x
        if y < miny: miny = y
        if x + w > maxx: maxx = x + w
        if y + h > maxy: maxy = y + h

    write_frame(img, rect=(minx, miny, maxx, maxy))

    return (minx, miny, maxx, maxy)

def crop(img, boundaries):
    """Crop the image to the given boundaries."""
    minx, miny, maxx, maxy = boundaries
    return img[miny:maxy, minx:maxx]

def autocrop_image(input_file, output_file=None, record_process=False):
    """Autocrop the photograph from the given image."""

    # global to track if process frames should be written
    global record
    record = record_process
    if record:
        os.makedirs('frames', exist_ok=True)

    if not output_file:
        parts = input_file.split('.')
        assert len(parts) > 1, "Can't automatically choose output name if there's no file extension!"
        output_file = '.'.join([*parts[:-1], 'cropped', parts[-1]])

    img = cv2.imread(input_file)
    write_frame(img)

    contours = get_contours(img)
    bounds = get_boundaries(img, contours)
    cropped = crop(img, bounds)
    if get_size(cropped) < 10000: 
        print("resulting image too small, skipping output")
        return # too small
    cv2.imwrite(output_file, cropped)

if __name__ == '__main__':
    parser = ArghParser()
    parser.set_default_command(autocrop_image)
    parser.dispatch()
