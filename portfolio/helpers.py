import hmac
import hashlib
import json
import os


def is_valid_signature(raw_body, received_sig):
    print("Received Signature : " received_sig)
    print("raw body:" raw_body)

    return hmac.compare_digest(computed_sig, received_sig.lower())