#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

"""Displays a rotating torus using the pyglet.graphics API.

This example uses the pyglet.graphics API to render an indexed vertex
list. The vertex list is added to a batch, allowing easy rendered
alongside other vertex lists with minimal overhead.

This example demonstrates:

 * Setting a 3D projection on a window by overriding the default
   on_resize handler
 * Enabling multisampling if available
 * Drawing simple 3D primitives using the pyglet.graphics API
 * Fixed-pipeline lighting
"""
# from math import pi, sin, cos

VERB = False
VERB = True

import sys
import numpy as np
import zmq

line_width = 3
RESOLUTION = 1000
z0 = .65 # in meter
s0 = .15 # normalized unit
VA_X = 30 * np.pi/180 # vertical visual angle (in radians) of the camera
VA_Y = 45 * np.pi/180 # horizontal visual angle (in radians) of the camera
screen_height, screen_width, viewing_distance  = .30, .45, z0
# https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
# fovy : Specifies the field of view angle, in degrees, in the y direction.
# on calcule
VA = 2. * np.arctan2(screen_height/2., viewing_distance) * 180. / np.pi
pc_min, pc_max = 0.1, 255.0
pc_min, pc_max = 0.001, 1000000.0
print(f'VA = {VA:.3f} deg')



#  Socket to talk to server
zmqcontext = zmq.Context()
print("Connecting to server…")
socket = zmqcontext.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def translate(message):
    x, y, s = message.split(', ')
    x, y, s = int(x), int(y), int(s) # str > int
    x, y, s = x/RESOLUTION, y/RESOLUTION, s/RESOLUTION
    x, y, s = x-.5, y-.5, s
    print(f'x, y, s (norm) = {x:.3f}, {y:.3f}, {s:.3f}')

    z = z0 * s0 / s
    x = - z * np.tan(x * VA_X)
    y = - z * np.tan(y * VA_Y)
    print(f'x, y, z (Eye) = {x:.3f}, {y:.3f}, {z:.3f}')
    return x, y, z

import pyglet
import pyglet.gl as gl
display = pyglet.canvas.get_display()
print ("DEBUG: display client says display" , display)
screens = display.get_screens()
print ("DEBUG: display client says screens" , screens)
for i, screen in enumerate(screens):
    print('Screen %d: %dx%d at (%d,%d)' % (i, screen.width, screen.height, screen.x, screen.y))
N_screen = len(screens) # number of screens
assert N_screen == 1 # we should be running on one screen only

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.window import Window
fullscreen = False
fullscreen = True
# Try and create a window with multisampling (antialiasing)
# config = gl.Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)
# window_0 = Window(resizable=True, fullscreen=fullscreen, config=config)
# window_0.projection = pyglet.window.Projection3D(fov=VA)
window_0 = Window(screen=screens[0], fullscreen=fullscreen, resizable=True, vsync = True)
# window_0.set_exclusive_mouse()
from pyglet.gl.glu import gluLookAt

def on_resize(width, height):
    gl.glViewport(0, 0, width*2, height*2) # HACK for retina display ?
    # gl.glEnable(gl.GL_BLEND)
    gl.glShadeModel(gl.GL_SMOOTH)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)#gl.GL_DONT_CARE)# gl.GL_NICEST)#
    # gl.glDisable(gl.GL_DEPTH_TEST)
    # gl.glDisable(gl.GL_LINE_SMOOTH)
    # gl.glColor3f(1.0, 1.0, 1.0)
    return pyglet.event.EVENT_HANDLED

window_0.on_resize = on_resize
window_0.set_visible(True)
window_0.set_mouse_visible(False)


# scene geometry
gl.gluPerspective(VA, 1.0*window_0.width/window_0.height, pc_min, pc_max)
gl.glEnable(gl.GL_LINE_STIPPLE)

axis_particles = []
axis_particles.append([screen_width/3, screen_height/4, 0,
                       screen_width/3, 3*screen_height/4, 0])
axis_particles.append([2*screen_width/3, screen_height/4, 0,
                  2*screen_width/3, 3*screen_height/4, 0])
axis_particles = np.array(axis_particles).T

screen_particles = []
screen_particles.append([0, 0, 0,
                        screen_width, 0, 0])
screen_particles.append([0, screen_height, 0,
                        screen_width, screen_height, 0])
screen_particles.append([screen_width, screen_height, 0,
                        screen_width, 0, 0])
screen_particles.append([0, 0, 0,
                         0, screen_height, 0])
screen_particles = np.array(screen_particles).T

# https://github.com/Yuriy-Leonov/Pyglet_z_axis_issue/blob/master/main.py


from pyglet.graphics import draw

@window_0.event
def on_draw():
    global my_cx, my_cy, my_cz
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    # print(rx, ry, rz)
    # gl.glRotatef(rz, 0, 0, 1)
    # gl.glRotatef(ry, 0, 1, 0)
    # gl.glRotatef(rx, 1, 0, 0)
    window_0.clear()

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    # https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml

    # fovy : Specifies the field of view angle, in degrees, in the y direction.
    # aspect :Specifies the aspect ratio that determines the field of view in the x direction. The aspect ratio is the ratio of x (width) to y (height).
    # zNear : Specifies the distance from the viewer to the near clipping plane (always positive).
    # zFar : Specifies the distance from the viewer to the far clipping plane (always positive).
    VA = 2. * np.arctan2(screen_height/2., my_cz) * 180. / np.pi

    gl.gluPerspective(VA, window_0.width/window_0.height, pc_min, pc_max)

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    # gluLookAt(eyex,eyey,eyez,centx,centy,centz,upx,upy,upz)
    gluLookAt(my_cx, my_cy, my_cz,
              screen_width/2, screen_height/2, 0,
              0, 1, 0)

    # gl.glMatrixMode(gl.GL_MODELVIEW)

    # lighting
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, vec(screen_width/2*0, screen_height/2, -screen_height*.0, 0))
    # gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, vec(.5, .5, 1))
    # gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, vec(1, 1, 1, 1))

    gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, vec(screen_width/2*2, screen_height/2, screen_height*.2, 0))


    batch.draw()

    # gl.glLineWidth(4)
    # # TODO : https://pyglet.readthedocs.io/en/latest/programming_guide/graphics.html#batched-rendering
    # gl.glColor3f(1., 1., 1.)
    #
    # gl.glColor3f(1., 0., 0.)
    # draw(2*2, gl.GL_LINES, ('v3f', axis_particles.T.ravel().tolist()))
    #
    # pyglet.graphics.draw(2*4, gl.GL_LINES, ('v3f', screen_particles.T.ravel().tolist()))


# def update(dt):
#     global rx, ry, rz
#     rx += dt * 1
#     ry += dt * 80
#     rz += dt * 30
#     rx %= 360
#     ry %= 360
#     rz %= 360

def vec(*args):
    return (gl.GLfloat * len(args))(*args)

def setup():
    # One-time GL setup
    lum = .1
    # gl.glClearColor(lum, lum, lum, 1)
    # gl.glColor3f(1, 0, 0)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glEnable(gl.GL_LIGHT1)


def create_torus(radius, inner_radius, slices, inner_slices, batch):
    # Create the vertex and normal arrays.
    vertices = []
    normals = []

    u_step = 2 * np.pi / (slices - 1)
    v_step = 2 * np.pi / (inner_slices - 1)
    u = 0.
    for i in range(slices):
        cos_u = np.cos(u)
        sin_u = np.sin(u)
        v = 0.
        for j in range(inner_slices):
            cos_v = np.cos(v)
            sin_v = np.sin(v)

            d = (radius + inner_radius * cos_v)
            x = screen_width/2 + d * cos_u
            y = screen_height/2 + d * sin_u
            z = screen_height*0.5 + inner_radius * sin_v

            nx = cos_u * cos_v
            ny = sin_u * cos_v
            nz = sin_v

            vertices.extend([x, y, z])
            normals.extend([nx, ny, nz])
            v += v_step
        u += u_step

    # Create a list of triangle indices.
    indices = []
    for i in range(slices - 1):
        for j in range(inner_slices - 1):
            p = i * inner_slices + j
            indices.extend([p, p + inner_slices, p + inner_slices + 1])
            indices.extend([p, p + inner_slices + 1, p + 1])

    # Create a Material and Group for the Model
    diffuse = [0.5, 0.0, 0.3, 1.0]
    ambient = [0.5, 0.0, 0.3, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    emission = [0.0, 0.0, 0.0, 1.0]
    shininess = 50
    material = pyglet.model.Material("", diffuse, ambient, specular, emission, shininess)
    group = pyglet.model.MaterialGroup(material=material)

    vertex_list = batch.add_indexed(len(vertices)//3,
                                    gl.GL_TRIANGLES,
                                    group,
                                    indices,
                                    ('v3f/static', vertices),
                                    ('n3f/static', normals))

    return pyglet.model.Model([vertex_list], [group], batch)

# setup scene
setup()
batch = pyglet.graphics.Batch()

# torus_model = create_torus(1, 0.3, 50, 30, batch=batch)
torus_model = create_torus(screen_width/10, screen_width/24, 50, 30, batch=batch)

rx = ry = rz = 0

import time
tic = time.time()

def update(dt):
    global my_cx, my_cy, my_cz

    message = "ERROR"
    tic = time.time()
    #  Get the reply.
    while (message == "ERROR"):
        print("Sending request … GO!")
        socket.send(b"GO!")

        message = socket.recv()
        message = message.decode()
        print(message)

        if message == "ERROR":
            print(message)
            sys.exit()

    x, y, z = translate(message)

    toc = time.time()

    print(f'FPS:{1/(toc-tic):.1f}')

    my_cx, my_cy, my_cz = screen_width/2 + y, screen_height/2 + x, z
    #my_cx, my_cy, my_cz = y, x, z
    if VERB:
        print(f'x, y, z (Eye) = {my_cx:.3f}, {my_cy:.3f}, {my_cz:.3f}')
        print(f'DEBUG {pyglet.clock.get_fps():.3f}  fps')


pyglet.clock.schedule(update)
pyglet.app.run()
