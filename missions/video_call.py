from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=3,
        icon="📹",
        name="Make a video call",
        description="Establish real-time video/audio communication.",
        payload="Video + Audio stream",
        decisions={
            "Transport": LayerDecision(
                layer="Transport",
                question="Choose protocol",
                options={"UDP": "Lower latency for real-time traffic", "TCP": "Reliable but may add delay"},
                correct_option="UDP",
                error_message="Latency spike due to retransmission delays.",
                repair_hint="Use UDP for this simplified real-time mission",
            )
        },
    )
