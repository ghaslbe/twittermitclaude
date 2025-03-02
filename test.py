import urllib.request
import urllib.parse
import json
import base64
import hmac
import hashlib
import time
import random
import string
import sys
import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="sk-ant-api03-ulLrYeWEPXIR4hLhyUP8DnDx6gM7fgC9mAJ9zo5W8KPddddddKyt7oEK-bgOUq9_qDGqhBOI8VCgDTvmw---L7pwAA",
)



def generate_nonce():
    """Generiert einen zufälligen Nonce-String"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

def make_twitter_request(api_key, api_secret, access_token, access_token_secret, text):
    # Twitter API Endpoint
    url = "https://api.twitter.com/2/tweets"
    
    # OAuth Parameter
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = generate_nonce()
    
    # Parameter für OAuth Signatur
    params = {
        'oauth_consumer_key': api_key,
        'oauth_nonce': oauth_nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': oauth_timestamp,
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }
    
    # Tweet Daten
    data = {
        'text': text
    }
    
    # Signatur erstellen
    base_string = '&'.join([
        'POST',
        urllib.parse.quote(url, safe=''),
        urllib.parse.quote('&'.join([
            f"{k}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted(params.items())
        ]), safe='')
    ])
    
    signing_key = '&'.join([
        urllib.parse.quote(api_secret, safe=''),
        urllib.parse.quote(access_token_secret, safe='')
    ])
    
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')
    
    # Authorization Header erstellen
    params['oauth_signature'] = signature
    auth_header = 'OAuth ' + ', '.join([
        f'{k}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in params.items()
    ])
    
    # Request erstellen
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    try:
        # Request ausführen
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            print("Tweet erfolgreich gepostet!")
            print(response_data)
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Fehler: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Fehler beim Posten: {str(e)}")

if __name__ == "__main__":
    # API Zugangsdaten
    API_KEY = "U6PUG0T7mzvCBi9yc31Tafhzu"
    API_SECRET = "Suk9S5L6Q2ihfCyyE2BJ5g2rFrIZeMnglhz7vHV8S1sBC9DqYo"
    ACCESS_TOKEN = "1896110843999182848-VKVfdFpISxAf2ypEMxzrIpUU0gB1f8"
    ACCESS_TOKEN_SECRET = "xZ4azlgkc2EQlL5nkwONbC0mlYCpTQ0VulKRncwlR8doW"


    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=20000,
        temperature=1,
        system="Antworte immer auf deutsch",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "generiere einen text mit max 120 zeichen zum thema umweltschutz"
                    }
                ]
            }
        ]
    )
    print(message.content)
    
    
    # Tweet Text aus Kommandozeilenargument
    tweet_text =  message.content[0].text+" #afd #cdu #csu"
    
    # Tweet senden
    make_twitter_request(
        api_key=API_KEY,
        api_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        text=tweet_text
    )
