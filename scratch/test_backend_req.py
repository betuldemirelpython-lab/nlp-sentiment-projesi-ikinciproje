import os, requests, json
url = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')
api_key = os.getenv('API_KEY')
headers = {'x-api-key': api_key} if api_key else {}
resp = requests.post(f"{url}/predict", json={"text": "I love this product!"}, headers=headers)
print('Status:', resp.status_code)
print('Body:', resp.text)
