from enum import Enum


class PlatformUserEnum(Enum):
    student = 'student'
    teacher = 'teacher'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)