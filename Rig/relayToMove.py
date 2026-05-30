import maya.cmds as cmds
from wombatAutoRig.src.core import Offset


def locRelayToMove(LocRelay):
    move = LocRelay.replace("LocRelay", "Loc") + "_Move"
    hook = LocRelay.replace("LocRelay", "Loc") + "_Hook"

    #disconnect the locrelay from the loc
    cmds.disconnectAttr(LocRelay + ".translate", hook + ".translate")
    cmds.disconnectAttr(LocRelay + ".rotate", hook + ".rotate")
    cmds.disconnectAttr(LocRelay + ".scale", hook + ".scale")

    #connect the move to the relay to get the transform of the loc
    Offset.offset(LocRelay, nbr=1)

    cmds.connectAttr(LocRelay + ".translate", move + ".translate")
    cmds.connectAttr(LocRelay + ".rotate", move + ".rotate")
    cmds.connectAttr(LocRelay + ".scale", move + ".scale")

if __name__ == "__main__":
    selection = cmds.ls(selection=True)
    for sel in selection:
        locRelayToMove(sel)