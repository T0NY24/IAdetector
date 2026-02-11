import requests
import os
import sys

# Disable proxies if any
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

url = 'http://localhost:5000/api/analyze_image'
file_path = r'c:\Users\anper\Downloads\ProyectoForenseUIDE\samples\test.png'

print(f"Testing API at: {url}")
print(f"Using image: {file_path}")

if not os.path.exists(file_path):
    print(f"❌ Error: File not found at {file_path}")
    sys.exit(1)

try:
    with open(file_path, 'rb') as f:
        files = {'image': ('test.png', f, 'image/png')}
        print("Sending request...")
        response = requests.post(url, files=files, timeout=600)  # Long timeout for model loading
        
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS: Analysis completed successfully.")
        print("Result Summary:")
        # Print relevant parts of the result
        print(f"  Verdict: {data.get('result', {}).get('verdict')}")
        print(f"  Confidence: {data.get('result', {}).get('confidence')}")
        print(f"  Technique: {data.get('result', {}).get('technique')}")
    else:
        print(f"❌ FAILED: Server returned {response.status_code}")
        print("Response:", response.text)
        sys.exit(1)

except Exception as e:
    print(f"❌ EXCEPTION: {e}")
    sys.exit(1)
