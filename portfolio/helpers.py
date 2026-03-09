import hmac
import hashlib
import json
import os
import urllib

def is_valid_signature(raw_body, received_sig):
    print(f"Received Signature : {received_sig}")
    print(f"raw body: {raw_body}")
    secret_key = os.environ.get("MID")
    data = raw_body.get("signatureKeys")
    data.pop(2)
    concat_values = "&".join(
        f"{key}={urllib.parse.quote(str(raw_body.get(key,'')))}" for key in data
        )

    
    print(f"Concat Values : {concat_values}" if concat_values else "NO Concat Values")

    computed_sig = hmac.new(
        secret_key.encode("utf-8"),
        concat_values.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    print(hmac.compare_digest(computed_sig, received_sig))