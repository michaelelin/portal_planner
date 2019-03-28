import math

def offset_line(x1, y1, x2, y2, offset):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    offset_x = dy * offset / dist
    offset_y = -dx * offset / dist
    return (x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y)
