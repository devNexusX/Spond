import asyncio
import aiohttp
import json
from config import username, password

async def debug_2fa_flow():
    """Debug the 2FA flow step by step"""
    
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        # Step 1: Initial login
        print("=== Step 1: Initial Login ===")
        login_url = "https://api.spond.com/core/v1/login"
        data = {"email": username, "password": password}
        
        async with session.post(login_url, json=data) as r:
            print(f"Status: {r.status}")
            print(f"Headers: {dict(r.headers)}")
            login_result = await r.json()
            print(f"Response: {login_result}")
            
        if "token" in login_result and "phoneNumber" in login_result:
            temp_token = login_result["token"]
            phone = login_result["phoneNumber"]
            print(f"\n2FA Required - SMS sent to: {phone}")
            
            # Get SMS code from user
            sms_code = input("Enter SMS code: ").strip()
            
            # Step 2: Try various 2FA verification approaches
            print("\n=== Step 2: Trying different 2FA approaches ===")
            
            # Approach A: POST to login with just token and sms
            print("\nApproach A: Login with token + smsCode")
            data_a = {"token": temp_token, "smsCode": sms_code}
            async with session.post(login_url, json=data_a) as r:
                print(f"Status: {r.status}")
                if r.status != 404:
                    try:
                        result = await r.json()
                        print(f"Response: {result}")
                    except:
                        text = await r.text()
                        print(f"Text response: {text}")
            
            # Approach B: POST to login with email, password, token, sms
            print("\nApproach B: Full login with token + smsCode")
            data_b = {"email": username, "password": password, "token": temp_token, "smsCode": sms_code}
            async with session.post(login_url, json=data_b) as r:
                print(f"Status: {r.status}")
                if r.status != 404:
                    try:
                        result = await r.json()
                        print(f"Response: {result}")
                    except:
                        text = await r.text()
                        print(f"Text response: {text}")
                        
            # Approach C: Check if there are any cookies or headers set
            print(f"\nSession cookies after login: {session.cookie_jar}")
            
            # Approach D: Try making a direct API call with the token
            print(f"\nApproach D: Direct API call with token")
            headers = {"Authorization": f"Bearer {temp_token}", "content-type": "application/json"}
            groups_url = "https://api.spond.com/core/v1/groups/"
            async with session.get(groups_url, headers=headers) as r:
                print(f"Groups API Status: {r.status}")
                if r.status != 404:
                    try:
                        result = await r.json()
                        print(f"Groups Response: {result}")
                    except:
                        text = await r.text()
                        print(f"Groups Text response: {text}")

if __name__ == "__main__":
    asyncio.run(debug_2fa_flow())