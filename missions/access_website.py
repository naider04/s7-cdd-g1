from simulator.models import LayerDecision, Mission


def build_mission() -> Mission:
    return Mission(
        mission_id=2,
        icon="🌐",
        name="Access a website",
        description="Resolve domain and request a web page from a remote server.",
        payload="GET https://www.example.com",
        decisions={
            "Application": LayerDecision(
                layer="Application",
                question="Choose web protocol",
                options={"HTTPS": "Secure web browsing", "SMTP": "Email sending protocol"},
                correct_option="HTTPS",
                error_message="Protocol mismatch: server expected HTTP/HTTPS request.",
                repair_hint="Use HTTPS for website access",
            )
        },
    )
