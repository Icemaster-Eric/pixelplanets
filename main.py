import pyglet
from pyglet.gl import glEnable, glBlendFunc, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
import numpy as np
import math
from noise import snoise3
from random import randint


window = pyglet.window.Window()


def rotate_point(x, y, z, ox, oy, oz, angle):
    rotation_matrix = [
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]]

    return np.dot([x - ox, y - oy, z - oz], rotation_matrix) + [ox, oy, oz]


class Planet:
    def __init__(self, size=128, rotation=0, light_source=(randint(0, 128), randint(0, 128)), light_intensity=0.5):
        self.pixels = np.zeros([size, size, 4], dtype=np.uint8)

        image_data = pyglet.image.ImageData(
            size, size, "RGBA", self.pixels.tobytes(), size*4
        )

        for x in range(size):
            for y in range(size):
                distance_to_center = math.dist((size/2, size/2), (x, y))

                if distance_to_center < size/2:
                    z = size/2 - distance_to_center

                    rx, ry, rz = rotate_point(x, y, z, size/2, size/2, 0, rotation)

                    distance_to_light = math.dist(light_source, (x, y))

                    lighting = min(1/((distance_to_light+1)/(light_intensity*100)), 1)

                    noise_level = snoise3(
                        rx/100, ry/100, rz/100, octaves=6, lacunarity=2.5, persistence=0.5
                    )

                    if noise_level < -0.3:
                        self.pixels[y, x, 0] = 60 * lighting
                        self.pixels[y, x, 1] = 100 * lighting
                        self.pixels[y, x, 2] = 235 * lighting

                    elif noise_level < 0:
                        self.pixels[y, x, 0] = 80 * lighting
                        self.pixels[y, x, 1] = 120 * lighting
                        self.pixels[y, x, 2] = 255 * lighting

                    elif noise_level < 0.1:
                        self.pixels[y, x, 0] = 178 * lighting
                        self.pixels[y, x, 1] = 145 * lighting
                        self.pixels[y, x, 2] = 0 * lighting

                    elif noise_level < 0.3:
                        self.pixels[y, x, 0] = 124 * lighting
                        self.pixels[y, x, 1] = 205 * lighting
                        self.pixels[y, x, 2] = 20 * lighting

                    elif noise_level < 0.6:
                        self.pixels[y, x, 0] = 0 * lighting
                        self.pixels[y, x, 1] = 128 * lighting
                        self.pixels[y, x, 2] = 0 * lighting

                    else:
                        self.pixels[y, x, 0] = 100 * lighting
                        self.pixels[y, x, 1] = 100 * lighting
                        self.pixels[y, x, 2] = 100 * lighting

                    self.pixels[y, x, 3] = 255

        data = np.flipud(self.pixels).tobytes()

        image_data.set_data("RGBA", size*4, data)

        self.image = image_data

        self.size = size

    def draw(self):
        self.image.blit(window.width/2 - self.size/2,
                        window.height/2 - self.size/2)


class Clouds:
    def __init__(self, size=128, rotation=0, offset=0):
        size = size + 30

        self.pixels = np.zeros([size, size, 4], dtype=np.uint8)

        image_data = pyglet.image.ImageData(
            size, size, "RGBA", self.pixels.tobytes(), size*4
        )

        for y in range(size):
            for x in range(size):
                distance_to_center = math.dist((size/2, size/2), (y, x))

                if distance_to_center < size/2:
                    z = size/2 - distance_to_center

                    rx, ry, rz = rotate_point(
                        x + offset, y + offset, z + offset, size/2, size/2, 0, rotation
                    )

                    noise_level = snoise3(
                        rx/100, ry/100, rz/100, octaves=6, lacunarity=1.8, persistence=0.8
                    )

                    if noise_level > 0.1:
                        self.pixels[y, x, 0] = 255
                        self.pixels[y, x, 1] = 255
                        self.pixels[y, x, 2] = 255
                        self.pixels[y, x, 3] = 100

        data = np.flipud(self.pixels).tobytes()

        image_data.set_data("RGBA", size*4, data)

        self.image = image_data
        
        self.size = size

    def draw(self):
        self.image.blit(window.width/2 - self.size/2,
                        window.height/2 - self.size/2)


@window.event
def on_draw():
    window.clear()

    planet.draw()
    clouds.draw()


def update(dt):
    global planet, clouds, rotation

    rotation += dt * 0.1
    rotation = rotation % (math.pi * 2)

    planet = Planet(size=size, rotation=rotation)
    clouds = Clouds(size=size-20, rotation=rotation, offset=offset)


if __name__ == "__main__":
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    rotation = 0.2
    offset = 30
    size = 128

    planet = Planet(size=size)
    clouds = Clouds(size=size-20, offset=offset)

    pyglet.clock.schedule_interval(update, 1/30)
    pyglet.app.run()
