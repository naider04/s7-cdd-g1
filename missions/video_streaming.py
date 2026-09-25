from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=6,
        icon="📺",
        name="Stream a video",
        description="Receive continuous video data with buffering behavior.",
        payload="Streaming chunks + playback buffer",
        decisions={
            "Session": LayerDecision(
                layer="Session",
                question="Select session state",
                options={"ESTABLISHED": "Ready to stream", "INTERRUPTED": "Session dropped"},
                correct_option="ESTABLISHED",
                error_message="Buffering occurred due to interrupted session.",
                repair_hint="Re-establish session",
            )
        },
    )
