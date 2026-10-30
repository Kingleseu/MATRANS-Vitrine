"""Projection commune au fond SVG et aux repères de la carte publique."""

MAP_WIDTH = 900
MAP_HEIGHT = 900
MAP_PADDING = 32
MAP_WEST = 12.2009869
MAP_EAST = 31.277423072584575
MAP_SOUTH = -13.459035
MAP_NORTH = 5.3919312


def project(longitude, latitude):
    usable_width = MAP_WIDTH - 2 * MAP_PADDING
    usable_height = MAP_HEIGHT - 2 * MAP_PADDING
    x = MAP_PADDING + (float(longitude) - MAP_WEST) / (MAP_EAST - MAP_WEST) * usable_width
    y = MAP_PADDING + (MAP_NORTH - float(latitude)) / (MAP_NORTH - MAP_SOUTH) * usable_height
    return x, y
