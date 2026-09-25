from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=5,
        icon="🎮",
        name="Play a multiplayer game",
        description="Exchange frequent low-latency position updates.",
        payload="Position update #001..#004",
        decisions={
            "Transport": LayerDecision(
                layer="Transport",
                question="Choose protocol",
                options={"UDP": "Fast updates; occasional loss tolerable", "TCP": "Reliable but can stall state updates"},
                correct_option="UDP",
                error_message="Gameplay stuttered while waiting for missing packets.",
                repair_hint="Use UDP for this mission",
            )
        },
    )
