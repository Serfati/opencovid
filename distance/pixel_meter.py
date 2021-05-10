import math
import numpy as np
import cv2

from lib.config import *

mouse_pressed = False
lengths = np.array([])
# data = np.array([])
temp_data = []

class DrawLineWidget(object):
    def __init__(self, img):
        self.original_image = img
        self.clone = self.original_image.copy()
        cv2.namedWindow('Pixel-Meter')
        cv2.setWindowProperty('Pixel-Meter', cv2.WND_PROP_TOPMOST, 2)  # set window always on top
        cv2.setMouseCallback('Pixel-Meter', self.extract_coordinates)
        self.dist = 0
        self.pixel_as_cm = 0
        # List to store start/end points
        self.image_coordinates = []

    def extract_coordinates(self, event, x, y, flags, parameters):
        global mouse_pressed
        # Record ending (x,y) coordintes on left mouse bottom release
        if event == cv2.EVENT_LBUTTONUP:
            mouse_pressed = False
            end = len(self.image_coordinates) - 1
            # print('Starting: {}, Ending: {}'.format(self.image_coordinates[0], self.image_coordinates[end]))
            x1 = self.image_coordinates[0][0]
            x2 = self.image_coordinates[end][0]
            y1 = self.image_coordinates[0][1]
            y2 = self.image_coordinates[end][1]
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            self.dist = dist
            # print('Distance: ' + str(dist))
            print(Cyan + "SETUP\nEnter Object of Reference size in CM:" + Bold + White)
            size_in_cm = input()
            try:
                if self.pixel_as_cm == 0:
                    self.pixel_as_cm = float(size_in_cm) / float(self.dist)
                # print('one pixel as cm: {:0.3f}'.format(self.pixel_as_cm))
            except ZeroDivisionError:
                self.pixel_as_cm = 100

            # Draw line
            self.clone = self.original_image.copy()
            cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[end], (107, 209, 67), 2, cv2.LINE_AA)
            cv2.imshow("Pixel-Meter", self.clone)

            pixels_in_meter = (dist / float(size_in_cm)) * 100

            global lengths
            global temp_data

            lengths = np.append(lengths, pixels_in_meter)
            temp_data.append((x1, y1))
            print(RESET+40*'=')
            print(f'\t\t{Magenta}{pixels_in_meter:.1f}{Bold} pixel/meter{RESET}')
            print(40*'=')

        if mouse_pressed:
            if event == cv2.EVENT_MOUSEMOVE:
                self.image_coordinates.append((x, y))
                # Draw line
                end = len(self.image_coordinates) - 1
                self.clone = self.original_image.copy()
                cv2.line(self.clone, self.image_coordinates[0], self.image_coordinates[end], (67, 76, 209), 2, cv2.LINE_AA)
                cv2.imshow("Pixel-Meter", self.clone)

        # Record starting (x,y) coordinates on left mouse button click
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x, y)]
            self.image_coordinates.append((x, y))
            mouse_pressed = True

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone


def convert(frame):

    if temp_data:
        data = np.array([*temp_data])
        return (lengths, data)

    img = frame.img
    height, width = img.shape[:2]
    max_height = 900
    max_width = 900
    # only shrink if img is bigger than required
    if max_height < height or max_width < width:
        # get scaling factor
        scaling_factor = max_height / float(height)
        if max_width / float(width) < scaling_factor:
            scaling_factor = max_width / float(width)
        # resize image
        img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
    draw_line_widget = DrawLineWidget(img)
    while True:
        cv2.imshow('Pixel-Meter', draw_line_widget.show_image())
        key = cv2.waitKey(10)
        # Close program with keyboard 'q'
        if key == 27 or key == ord('q'):
            cv2.destroyWindow("Pixel-Meter")
            data = np.array([*temp_data])
            return (lengths, data)
