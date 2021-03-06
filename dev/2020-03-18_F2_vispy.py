# -*- coding: utf-8 -*-
import numpy as np

import time

# https://github.com/vispy/vispy/blob/master/examples/basics/visuals/box.py
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Simple demonstration of Box visual.
"""

RESOLUTION = 1000

n_x = 1600
n_y = 800

# n_x = 800
# n_y = 550

import zmq
import sys
from vispy import app, gloo, visuals
from vispy.geometry import create_box
from vispy.visuals.transforms import MatrixTransform

class Canvas(app.Canvas):

    def __init__(self, n_x=n_x, n_y=n_y):
        # screen
        app.Canvas.__init__(self,
                            keys='interactive',
                            size=(n_x, n_y), fullscreen=True)
        self.n_x, self.n_y = n_x, n_y

        # capture
        self.zmqcontext = zmq.Context()

        #  Socket to talk to server
        print("Connecting to local server…")
        self.socket = self.zmqcontext.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")

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

        self.THETA = 90
        self.THETA = -45
        self.SCALE = .5 * np.sqrt(self.n_x**2 + self.n_y**2)
        self.theta = 0
        self.phi = 0
        self.x = 0
        self.y = 0
        self.s = 1

        self.transform = MatrixTransform()

        self.box.transform = self.transform
        self.show()

        self.timer = app.Timer(connect=self.rotate)
        self.timer.start(0.016)

    def rotate(self, event):
        # self.theta += .5
        # self.phi += .5
        self.theta = self.x * self.THETA
        self.phi = self.y * self.THETA
        self.transform.reset()
        self.transform.rotate(self.theta, (0, 0, 1))
        self.transform.rotate(self.phi, (0, 1, 0))
        scale = self.s * self.SCALE
        self.transform.scale((scale, scale, 0.001))
        self.transform.translate((self.n_x/2, self.n_y/2))
        self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        self.box.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, ev):
        message = "ERROR"
        tic = time.time()
        #  Get the reply.
        while (message == "ERROR"):
            print("Sending request … GO!")
            self.socket.send(b"GO!")

            message = self.socket.recv()
            message = message.decode()
            print(message)

            if message == "ERROR":
                print(message)
                app.quit()
                sys.exit()

        x, y, s = message.split(', ')
        x, y, s = int(x), int(y), int(s) # str > int
        x, y, s = x/RESOLUTION, y/RESOLUTION, s/RESOLUTION
        x, y, s = 2*x-1, 2*y-1, s
        print(f'x, y, s (norm) = {x:.3f}, {y:.3f}, {s:.3f}')
        self.x, self.y, self.s = x, y, s
        gloo.clear(color='white', depth=True)
        self.box.draw()
        toc = time.time()

        print(f'FPS:{1/(toc-tic):.1f}')

win = Canvas()
app.run()
