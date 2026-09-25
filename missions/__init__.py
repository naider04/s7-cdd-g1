"""
Missions package registry for the OSI Communication Simulator.
Exports the 4 core interactive missions.
"""

from typing import List, Type
from missions.base_mission import BaseMission
from missions.mission1_file import MissionFileTransfer
from missions.mission2_web import MissionWebAccess
from missions.mission3_videocall import MissionVideoCall
from missions.mission4_text import MissionTextMessage

MISSION_CLASSES: List[Type[BaseMission]] = [
    MissionFileTransfer,
    MissionWebAccess,
    MissionVideoCall,
    MissionTextMessage,
]


def get_all_missions() -> List[BaseMission]:
    """Instantiate fresh instances of the 4 missions."""
    return [cls() for cls in MISSION_CLASSES]


def get_mission_by_id(mission_id: int) -> BaseMission:
    """Retrieve a fresh instance of a mission by its numeric ID (1-4)."""
    for cls in MISSION_CLASSES:
        inst = cls()
        if inst.mission_id == mission_id:
            return inst
    raise ValueError(f"ID de misión desconocido: {mission_id}")
