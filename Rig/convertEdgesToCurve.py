import maya.cmds as cmds

def edges_to_single_curve_transform():
    sel = cmds.ls(selection=True, flatten=True)
    if not sel:
        cmds.warning("Please select polygon edges.")
        return

    edges = cmds.filterExpand(sel, selectionMask=32)
    if not edges:
        cmds.warning("Selection must contain polygon edges.")
        return

    remaining = set(edges)
    edge_groups = []

    while remaining:
        current = remaining.pop()
        stack = [current]
        group = {current}

        while stack:
            edge = stack.pop()

            verts = cmds.polyListComponentConversion(edge, fromEdge=True, toVertex=True)
            verts = cmds.ls(verts, flatten=True)

            connected = cmds.polyListComponentConversion(verts, fromVertex=True, toEdge=True)
            connected = cmds.ls(connected, flatten=True)

            for e in connected:
                if e in remaining:
                    remaining.remove(e)
                    group.add(e)
                    stack.append(e)

        edge_groups.append(list(group))

    curves = []

    for group in edge_groups:
        cmds.select(group, replace=True)
        curve = cmds.polyToCurve(form=2, degree=1)[0]
        curves.append(curve)

    cmds.select(clear=True)

    if not curves:
        return

    # First curve becomes main transform
    main_curve = curves[0]

    for curve in curves[1:]:
        shapes = cmds.listRelatives(curve, shapes=True, fullPath=True) or []
        for shape in shapes:
            cmds.parent(shape, main_curve, shape=True, relative=True)

        cmds.delete(curve)

    cmds.delete(main_curve, constructionHistory=True)

    cmds.select(main_curve)
    print("Created curve with {} shapes.".format(len(edge_groups)))

    return main_curve


edges_to_single_curve_transform()