from __future__ import annotations

class Point:
    @classmethod
    def FromTuple(cls, tup) -> Point:
        return Point(tup[0], tup[1])

    @classmethod
    def Copy(cls, point) -> Point:
        return Point(point.X, point.Y)

    def __init__(self, *args):
        if len(args) == 0:
            self.X = 0
            self.Y = 0
        elif len(args) == 1 and isinstance(args[0], Point):
            self.X = args[0].X 
            self.Y = args[0].Y
        elif len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 2:
            self.X = args[0][0]
            self.Y = args[0][1]
        elif len(args) == 2 and (isinstance(args[0], int) or isinstance(args[0], float)) \
            and (isinstance(args[1], int) or isinstance(args[1], float)):
            self.X = args[0]
            self.Y = args[1]
        else:
            raise TypeError()

    def __getitem__(self, index):
        if index == 0:
            return self.X
        elif index == 1:
            return self.Y
        else:
            raise IndexError()

    def __setitem__(self, index, value):
        if index == 0:
            self.X = value
        elif index == 1:
            self.Y = value
        else:
            raise IndexError()
        
    def __eq__(self, other:Point):
        if not isinstance(other, Point):
            return False
        return self.X == other.X and self.Y == other.Y

    def __sub__(self, other) -> Point:
        return Point(self.X - other.X, self.Y - other.Y)

    def __add__(self, other) -> Point:
        return Point(self.X + other.X, self.Y + other.Y)
    
    def __mul__(self, scalar) -> Point:
        return Point(self.X * scalar, self.Y * scalar)

    def __repr__(self):
        return f'<Point({self.X}, {self.Y})>'

    def __str__(self):
        return repr(self)

    def manhattan_distance(self, other:Point):
        return abs(self.X - other.X) + abs(self.Y - other.Y)
        
    def to_json(self, version):
        if version == 1:
            return [self.X, self.Y]
        if version == 2:
            return [self.X, self.Y]

    def ToTuple(self): 
        return (self.X, self.Y)
