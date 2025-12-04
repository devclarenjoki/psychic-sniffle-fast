import requests

as2 = requests.get("https://sandbox-pay.fonbnk.com")

print(as2.text)