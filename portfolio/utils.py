def validateSignature(request, secret):
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