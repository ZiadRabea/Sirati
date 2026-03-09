import hmac
import hashlib
import os

def is_valid_signature(raw_body, received_sig):
    """
    Verifies that the request came from Kashier by hashing the 
    raw body with your secret key.
    """
    secret = os.environ.get('KASHIER_SECRET') # or settings.KASHIER_SECRET
    if not secret or not received_sig:
        return False
        
    computed_sig = hmac.new(
        secret.encode('utf-8'),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    # Use compare_digest to prevent timing attacks
    return hmac.compare_digest(computed_sig, received_sig)