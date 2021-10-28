from ..models import Door


def calculate_door(door_pk):
    print(door_pk)
    door = Door.objects.get(pk=door_pk)
    if door.material:
        price = door.material.price
    else:
        price = 1
    width = door.width * price
    height = door.height * price
    depth = door.depth * price
    if door.sash:
        sash = door.sash.price
    else:
        sash = 1
    if door.style:
        style = door.style.price
    else:
        style = 1
    if door.closer:
        closer = door.closer.price
    else:
        closer = 0
    sum = width + height + depth + sash + style + closer
    return sum