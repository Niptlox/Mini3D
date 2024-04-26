"""
Перед запуском не забудьте скачать библиотеки. Через командную строку:
python -m pip install -U pygame, cmake, openmesh
"""
import math, openmesh, pygame
from pygame import Vector3


def rotate_point(point, rot):
    return point.rotate_z_rad(rot.z).rotate_y_rad(rot.y).rotate_x_rad(rot.x)


class Object3D:
    def __init__(self, position, rotation, points, faces, color=(200, 200, 200)):
        self.position = Vector3(position)
        self.rotation = Vector3(rotation)
        self.points = points
        self.faces = faces
        self.color = color

    def show(self, camera):
        points2d = [camera.point_to_2d(self.position + rotate_point(point, self.rotation)) for point in self.points]
        for face in self.faces:
            face_points = [points2d[num] for num in face]
            if all(face_points): pygame.draw.lines(camera.surface, self.color, True, face_points)


def open_obj(filename, position, color=(200, 200, 200), scale=1):
    mesh = openmesh.read_trimesh(filename)
    points = [Vector3(*mesh.point(p)) * scale for p in mesh.vertices()]
    faces = [[vh.idx() for vh in mesh.fv(fh)] for fh in mesh.faces()]
    return Object3D(position, Vector3(0, 0, 0), points, faces, color=color)


class Camera(Object3D):
    def __init__(self, surface, position, rotation, background=(10, 10, 10), fov=math.pi / 3):
        super().__init__(position, rotation, [], [], color=background)
        self.surface = surface
        self.half_width, self.half_height = self.surface.get_width() / 2, self.surface.get_height() / 2
        self.surface_rect = pygame.Rect((0, 0), self.surface.get_size())
        self.focus = math.tan(fov / 2) * self.half_width

    def point_to_2d(self, point):
        vec = rotate_point(point - self.position, self.rotation)
        z = 1e-9 if vec.z == 0 else vec.z
        x, y = self.focus * vec[0] / z + self.half_width, self.half_height - self.focus * vec[1] / z
        if self.surface_rect.collidepoint((x, y)) and z > 0: return x, y
        return None


if __name__ == '__main__':
    screen = pygame.display.set_mode((1200, 680))
    objects = [open_obj('monkey.obj', Vector3(0, 0, 4), scale=2), open_obj('monkey.obj', Vector3(5, 0, 6), scale=1)]
    camera = Camera(screen, Vector3(0, 0, 0), Vector3(0, 0, 0))
    while True:
        [exit() for _ in pygame.event.get(pygame.QUIT)]
        screen.fill(camera.color)
        [obj.show(camera) for obj in objects]
        objects[0].rotation += Vector3(0, 0.003, 0)
        pygame.display.flip()
