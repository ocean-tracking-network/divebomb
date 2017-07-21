'''
DiveShape
---------
DiveShape is an enumeration for classifying dives.
'''
from enum import Enum
class DiveShape(Enum):
    def __str__(self):
        return str(self.value)

    SQUARE = 'square'
    VSHAPE = 'v-shape'
    LEFTSKEW = 'left skewed'
    RIGHTSKEW = 'right skewed'
    OTHER = 'other'
    WIGGLE = 'wiggle'
    FLAT = 'flat'
    SHALLOW = 'shallow'
