from .access_website import build_mission as website_mission
from .large_file import build_mission as large_file_mission
from .multiplayer_game import build_mission as multiplayer_game_mission
from .send_email import build_mission as email_mission
from .text_message import build_mission as text_message_mission
from .video_call import build_mission as video_call_mission
from .video_streaming import build_mission as video_stream_mission


def all_missions():
    return [
        large_file_mission(),
        website_mission(),
        video_call_mission(),
        email_mission(),
        multiplayer_game_mission(),
        video_stream_mission(),
        text_message_mission(),
    ]
