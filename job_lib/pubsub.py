import base64
import json


def extract_message_from_pubsub_request(request):
    message_data = request.data.get("message", {}).get("data")
    if not message_data:
        return {}

    payload = base64.b64decode(message_data)
    return json.loads(payload.decode("utf-8"))
