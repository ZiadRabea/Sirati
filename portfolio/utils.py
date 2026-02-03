import hmac
import hashlib
import requests
from io import BytesIO
from django.core.mail import EmailMessage
def validate_signature(request, secret):
  queryString = ""
  for key in request:
      if key == "signature" or key == "mode":
          continue
      queryString += "&" + f"{key}=" + request[key]

  queryString = queryString[1:]  # Remove the initial '&'
  secret = bytes(secret, 'utf-8')
  queryString = queryString.encode()
  signature = hmac.new(secret, queryString, hashlib.sha256).hexdigest()

  return signature == request.get("signature")

def send_email_with_link(subject, body, to_email, file_url):
    """Downloads a file from a URL and sends it as an email attachment."""
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # raise error if download failed
        file_data = BytesIO(response.content)
        filename = file_url.split("/")[-1]  # extract filename from URL
    except Exception as e:
        print(f"Error downloading file: {e}")
        file_data = None
        filename = None

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[to_email]
    )

    if file_data and filename:
        email.attach(filename, file_data.read())

    email.send(fail_silently=False)