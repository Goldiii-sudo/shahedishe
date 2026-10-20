import urllib.request
import json
import sys
from tools.screen import capture_screen, pil_to_base64

clean_img = capture_screen()
clean_b64 = pil_to_base64(clean_img)

payload = {
    'model': 'gemini-4-argon',
    'messages': [{
        'role': 'user',
        'content': [
            {
                'type': 'text',
                'text': 'The image resolution is exactly 1920x1080. Locate the input field / prompt box on screen. Return only JSON: {"x": <int>, "y": <int>}'
            },
            {
                'type': 'image_url',
                'image_url': {'url': 'data:image/jpeg;base64,' + clean_b64}
            }
        ]
    }],
    'max_tokens': 100
}

req = urllib.request.Request(
    'http://localhost:8083/v1/chat/completions',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Authorization': 'Bearer sk-gemini-argon-local', 'Content-Type': 'application/json'}
)

resp = urllib.request.urlopen(req, timeout=30)
d = json.loads(resp.read().decode('utf-8'))
print('DETECTED COORDINATE:', d['choices'][0]['message']['content'])
