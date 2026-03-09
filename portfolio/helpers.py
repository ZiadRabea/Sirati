import hmac
import hashlib
import json
import os


def is_valid_signature(raw_body, received_sig):
    secret = os.environ.get("KASHIER_SECRET")
    if not secret or not received_sig:
        return False

    body = json.loads(raw_body)
    data = body.get("data", {})

    signature_keys = data.get("signatureKeys", [])

    parts = []
    for key in signature_keys:
        value = data.get(key, "")
        parts.append(f"{key}={value}")

    message = "&".join(parts)

    computed_sig = hmac.new(
        secret.encode("ascii"),
        message.encode("ascii"),
        hashlib.sha256
    ).hexdigest().lower()

    return hmac.compare_digest(computed_sig, received_sig.lower())