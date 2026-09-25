from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=4,
        icon="📧",
        name="Send an email",
        description="Send an email message to Person B.",
        payload="Subject: Hello\nBody: OSI mission email",
        decisions={
            "Application": LayerDecision(
                layer="Application",
                question="Choose protocol",
                options={"SMTP": "Send email", "IMAP": "Retrieve email"},
                correct_option="SMTP",
                error_message="Email was not sent because retrieval protocol was selected.",
                repair_hint="Switch to SMTP",
            )
        },
    )
