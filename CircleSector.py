class CircleSector:
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    @staticmethod
    def positive_mod(i):
        return (i % 65536 + 65536) % 65536

    def initialize(self, point):
        self.start = point
        self.end = point

    def is_enclosed(self, point):
        return CircleSector.positive_mod(point - self.start) <= CircleSector.positive_mod(self.end - self.start)

    @staticmethod
    def overlap(sector1, sector2):
        return (CircleSector.positive_mod(sector2.start - sector1.start) <= CircleSector.positive_mod(sector1.end - sector1.start)) or \
               (CircleSector.positive_mod(sector1.start - sector2.start) <= CircleSector.positive_mod(sector2.end - sector2.start))

    def extend(self, point):
        if not self.is_enclosed(point):
            if CircleSector.positive_mod(point - self.end) <= CircleSector.positive_mod(self.start - point):
                self.end = point
            else:
                self.start = point
