import copy
def loadFloorPlan(filename):
    with open(filename, "r", encoding="utf-8") as f:
        fileString = f.read()
    floorPlan = []
    floorRow = []
    # 2d list
    firstLine = True

    for line in fileString.splitlines():
        if firstLine:
            firstLine = False
            continue
        for value in line.split(','):
            floorRow = floorRow + [int(value)]
        floorPlan = floorPlan + [copy.copy(floorRow)]
        floorRow.clear()

    return floorPlan


# print(loadFloorPlan('./Floorplan.csv'))
