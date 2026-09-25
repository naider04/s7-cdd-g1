from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=1,
        icon="📁",
        name="Send a large file",
        description="Send a 500 MB video to Person B with reliability focus.",
        payload="video.mp4 (500 MB)",
        decisions={
            "Transport": LayerDecision(
                layer="Transport",
                question="Choose protocol",
                options={"TCP": "Reliable and ordered delivery", "UDP": "Low overhead, no retransmission"},
                correct_option="TCP",
                error_message="Large file transfer became incomplete due to missing retransmission.",
                repair_hint="Change protocol to TCP",
            )
        },
    )
