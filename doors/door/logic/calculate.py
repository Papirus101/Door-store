from ..models import Door


def calculate_door(door_pk):
    door = Door.objects.get(pk=door_pk)
    price = door.material.price
    width = door.width * price
    height = door.height * price
    depth = door.depth * price
    sash = door.sash.price
    style = door.style.price
    if door.closer:
        closer = door.closer.price
    else:
        closer = 0
    sum = width + height + depth + sash + style + closer
    return sum