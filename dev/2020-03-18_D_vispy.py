# -*- coding: utf-8 -*-
import numpy as np
import cv2
#
#
#
# import dlib
# class FaceExtractor:
#     def __init__(self, N_X, N_Y):
#         import dlib
#         self.detector = dlib.get_frontal_face_detector()
#         self.screen_size = N_X**2 + N_Y**2
#
#     def center_normalized(self, frame):
#         N_X, N_Y, three = frame.shape
#         dets = self.detector(frame, 1)
#         if len(dets) > 0:
#             bbox = dets[0]
#             t, b, l, r = bbox.top(), bbox.bottom(), bbox.left(), bbox.right()
#             x, y, s = t + (b-t)/2, l + (r-l)/2, (b-t)**2 + (r-l)**2
#             return 2*x/N_X - 1, 2*y/N_Y - 1, s / self.screen_size
#         else:
#             return 0, 0, 0


import time

# https://github.com/vispy/vispy/blob/master/examples/basics/visuals/box.py
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Simple demonstration of Box visual.
"""

from vispy import app, gloo, visuals
from vispy.geometry import create_box
from vispy.visuals.transforms import MatrixTransform
class Canvas(app.Canvas):

    def __init__(self, n_x=800, n_y=550):
        # screen
        self.n_x, self.n_y = n_x, n_y
        app.Canvas.__init__(self, keys='interactive', size=(n_x, n_y))
        # capture
        # self.vc = cv2.VideoCapture(0)
        # rgb_frame = self.grab()
        # self.N_X, self.N_Y, three = rgb_frame.shape
        # self.f = FaceExtractor(self.N_X, self.N_Y)


        vertices, faces, outline = create_box(width=1, height=1, depth=1,
                                              width_segments=4,
                                              height_segments=8,
                                              depth_segments=16)

        self.box = visuals.BoxVisual(width=1, height=1, depth=1,
                                     width_segments=4,
                                     height_segments=8,
                                     depth_segments=16,
                                     vertex_colors=vertices['color'],
                                     edge_color='b')

        self.THETA = np.pi / 4
        self.theta = 0
        self.phi = 0
        self.x = 0
        self.y = 0

        self.transform = MatrixTransform()

        self.box.transform = self.transform
        self.show()

        self.timer = app.Timer(connect=self.rotate)
        self.timer.start(0.016)


    def grab(self, DS=4):
        ret, frame = self.vc.read()# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        return frame[::DS, ::DS, ::-1]# Find all the faces in the current frame of video

    def rotate(self, event):
        self.theta += .5
        self.phi += .5
        # self.theta = self.x * self.THETA
        # self.phi = self.y * self.THETA
        self.transform.reset()
        self.transform.rotate(self.theta, (0, 0, 1))
        self.transform.rotate(self.phi, (0, 1, 0))
        self.transform.scale((100, 100, 0.001))
        self.transform.translate((200, 200))
        self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        self.box.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, ev):
        tic = time.time()
        # Grab a single frame of video
        # rgb_frame = self.grab()

        # detect face and extract position
        # self.x, self.y, self.s = self.f.center_normalized(rgb_frame)
        # print(f'x, y, s (norm) = {x:.3f}, {y:.3f}, {s:.3f}')


        gloo.clear(color='white', depth=True)
        self.box.draw()
        toc = time.time()

        print(f'FPS:{1/(toc-tic):.1f}')

win = Canvas()
app.run()
