import hmac
import hashlib
import json
import os


def is_valid_signature(raw_body, received_sig):
    print(f"Received Signature : {received_sig}")
    print(f"raw body: {raw_body}")

    data = raw_body.get("signatureKeys")
    
    concat_values = ""
    for key in data:
        # Get the value of this key from data
        value = raw_body.get(key, "")
        concat_values += str(value)
    
    print(concat_values if concat_values else "NO ConCAT Values")

    return None