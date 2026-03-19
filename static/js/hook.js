function buyProduct(productType, productamount, hash_string, mid, orderid, encoded_url ) {
  const emailInput = document.getElementById('emailInput');
  const email = emailInput.value.trim();
  const emailError = document.getElementById('emailError');

  if (!email || !email.includes('@')) {
    alert("يرجى إدخال البريد الاليكتروني بالأعلى لاستلام الكتاب")
    emailError.textContent = "يرجى إدخال بريد إلكتروني صحيح";
    return;
  } else {
    emailError.textContent = "";
  }

  let amount, hashString;
    amount = productamount;
    hashString = hash_string;

  const paymentUrl = "https://payments.kashier.io/?" +
    "merchantId="+ String(mid) +
    "&orderId="+ String(orderid) +
    "&amount=" + String(amount) +
    "&currency=EGP" +
    "&hash=" + String(hashString) +
    "&mode=" + "live" +
    "&display=en&enable3DS=true"+
    "&merchantRedirect="+ String(encoded_url) +
    "&serverWebhook=https://www.sirati.space/kashier/bookwebhook/" + productType + "/" + email +
    "&notes=''";

  window.location.href = paymentUrl;
}