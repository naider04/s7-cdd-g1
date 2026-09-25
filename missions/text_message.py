from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=7,
        icon="💬",
        name="Send a text message",
        description="Send multilingual text with correct encoding.",
        payload="¡Hola María! ¿Cómo estás?",
        decisions={
            "Presentation": LayerDecision(
                layer="Presentation",
                question="Choose encoding",
                options={"UTF-8": "Supports multilingual text", "ASCII": "Limited character set"},
                correct_option="UTF-8",
                error_message="Encoding mismatch caused corrupted characters.",
                repair_hint="Use UTF-8",
            )
        },
    )
