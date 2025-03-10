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

def generate_nonce():
    """Generiert einen zufälligen Nonce-String"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

def call_anthropic_api(api_key, prompt, model="claude-3-7-sonnet-20250219", max_tokens=20000, temperature=1, system="Antworte immer auf deutsch"):
    """Ruft die Anthropic API direkt über HTTP auf"""
    url = "https://api.anthropic.com/v1/messages"
    
    # API Request Daten
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": prompt if isinstance(prompt, list) else [{"type": "text", "text": prompt}]
            }
        ]
    }
    
    # Request Header
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    try:
        # Request erstellen
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        # Request ausführen
        with urllib.request.urlopen(request) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Fehler: {e.code}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Fehler bei der Anfrage: {str(e)}")
        return None

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
    # API Zugangsdaten für Anthropic
    ANTHROPIC_API_KEY = "sk-ant-api03-ulLrYeWEPXIR4hLhJYTjExxxxONKyt7oEK-bgOUq9_qDGqhBOI8VCgDTvmw---L7pwAA"
    
    # API Zugangsdaten für Twitter
    API_KEY = "U6PUG0T7mzxxxxxxxxvCBihzu"
    API_SECRET = "Suk9S5L6Q2ihvxxxxxxxxxxHV8S1sBC9DqYo"
    ACCESS_TOKEN = "189611084399xxxxxxxxx918rIpUU0gB1f8"
    ACCESS_TOKEN_SECRET = "xZ4azlgkcccccccxxxxxpTQ0VulKRncwlR8doW"

    # Anthropic API aufrufen
    prompt = "generiere einen text mit max 120 zeichen zum thema umweltschutz"
    response = call_anthropic_api(ANTHROPIC_API_KEY, prompt)
    
    if response and "content" in response:
        # Text aus der Antwort extrahieren
        if isinstance(response["content"], list) and len(response["content"]) > 0:
            generated_text = response["content"][0]["text"]
            print(generated_text)
            
            # Tweet senden
            tweet_text = generated_text + " #umweltschutz"
            
            # Prüfen, ob der Tweet die maximale Länge überschreitet
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
                
            make_twitter_request(
                api_key=API_KEY,
                api_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_TOKEN_SECRET,
                text=tweet_text
            )
        else:
            print("Unerwartetes Antwortformat von Anthropic")
    else:
        print("Keine Antwort von Anthropic erhalten")
