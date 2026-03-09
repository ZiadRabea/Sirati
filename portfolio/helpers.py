import hmac
import hashlib
import json
import os


def is_valid_signature(raw_body, received_sig):
    print(f"Received Signature : {received_sig}")
    print(f"raw body: {raw_body}")

    data = raw_body.get("signatureKeys")
    
    concat_values = "&".join(f"{key}={data.get(key,'')}" for key in keys)
    
    print(f"Concat Values : {concat_values}")
