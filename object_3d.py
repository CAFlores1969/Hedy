import pygame
from matrix_functions import *
from numba import njit


@njit(fastmath=True)
def any_func(arr, a, b):
    return numpy.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render, vertices='', faces='', colorLine='orange'):
        self.render = render
        self.vertices = numpy.array(vertices)
        self.faces = faces
        self.translate([0.0001, 0.0001, 0.0001])

        self.font = pygame.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pygame.Color(colorLine), face) for face in self.faces]
        self.movement_flag, self.draw_vertices = True, False #Activa rotacion y ver los puntos de vertices
        self.label = ''

    def draw(self, speedRot=0.004, colorLine=(0, 255, 0)):
        ###self.screen_projection()
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            polygon = vertices[face]
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                pygame.draw.polygon(self.render.screen, colorLine, polygon, 1)
                if self.label:
                    text = self.font.render(self.label[index], True, pygame.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for vertex in vertices:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pygame.draw.circle(self.render.screen, pygame.Color('white'), vertex, 2)

        ###self.movement()
        if self.movement_flag:
            #print(pygame.time.get_ticks() % 0.005)
            self.rotate_y(speedRot) #Velocidad de rotacion
            #self.rotate_y(-(pygame.time.get_ticks() % 0.005))

    def translate(self, pos):
        #@ multiplica matrices
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)


class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertices = numpy.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = numpy.array([(0, 1), (0, 2), (0, 3)])
        self.colors = [pygame.Color('red'), pygame.Color('green'), pygame.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
        self.draw_vertices = False
        self.label = 'XYZ'
