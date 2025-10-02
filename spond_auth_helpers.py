"""
Authentication helpers for Spond API that handle 2FA and web tokens.
"""

import asyncio
import json
import os
import base64
from datetime import datetime
from spond import spond


class TokenBasedSpond(spond.Spond):
    """Spond class that uses a pre-existing web token to avoid login attempts"""
    
    def __init__(self, username: str, password: str, token: str = None):
        super().__init__(username, password)
        self._token_tested = False
        if token:
            self.token = token
            print(f"🔑 Loaded web token (expires at some point - monitor for 401 errors)")
    
    async def login(self) -> None:
        """Override login to use existing token and avoid fresh authentication"""
        if self.token and not self._token_tested:
            # Test token only once to minimize API calls
            print("🧪 Testing web token (one-time check)...")
            if await self._test_token():
                print("✅ Web token is valid - no authentication needed!")
                self._token_tested = True
                return
            else:
                print("❌ Web token expired or invalid")
                self.token = None
                self._token_tested = True
        elif self.token and self._token_tested:
            # Token was already validated, trust it
            print("✅ Using previously validated web token")
            return
        
        # No valid token - this is where we'd normally do fresh login
        # But we want to avoid this to prevent lockouts
        print("🚨 CRITICAL: No valid web token available!")
        print("� Please get a fresh token from web login:")
        print("   1. Go to https://spond.com and log in")
        print("   2. Run 'python web_token_extractor.py'")
        print("   3. Re-run this script")
        raise Exception("No valid authentication token - please extract from web login")
    
    async def _test_token(self) -> bool:
        """Test if the current token works with minimal API impact"""
        try:
            # Use a lightweight endpoint to test
            url = f"{self.api_url}groups/"
            async with self.clientsession.get(url, headers=self.auth_headers) as r:
                if r.status == 200:
                    return True
                elif r.status == 401:
                    print("🔓 Token authentication failed (401 Unauthorized)")
                    return False
                else:
                    print(f"⚠️  Unexpected status code: {r.status}")
                    return False
        except Exception as e:
            print(f"❌ Token test failed: {e}")
            return False


class InteractiveSpond(spond.Spond):
    """Extended Spond class that handles interactive 2FA input"""
    
    async def _get_2fa_code(self, phone_number: str) -> str:
        """Prompt user for 2FA code via console input"""
        print(f"\n🔐 Two-factor authentication required!")
        print(f"📱 SMS code has been sent to: {phone_number}")
        print("Please check your phone and enter the verification code.")
        
        # Use asyncio to handle input without blocking
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Run input in a separate thread to avoid blocking the async loop
            sms_code = await loop.run_in_executor(executor, lambda: input("Enter SMS verification code: ").strip())
        
        if not sms_code:
            raise Exception("SMS code cannot be empty")
            
        return sms_code


def analyze_jwt_token(token: str) -> dict:
    """Safely analyze JWT token without making API calls"""
    try:
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Not a valid JWT format"}
        
        # Decode the payload (second part) - add padding if needed
        payload = parts[1]
        # Add padding to make length multiple of 4
        payload += '=' * (4 - len(payload) % 4)
        
        decoded = base64.b64decode(payload)
        payload_data = json.loads(decoded)
        
        # Check expiry if present
        result = {"payload": payload_data}
        if "exp" in payload_data:
            exp_time = datetime.fromtimestamp(payload_data["exp"])
            now = datetime.now()
            result["expires_at"] = exp_time.isoformat()
            result["is_expired"] = now > exp_time
            result["time_remaining"] = str(exp_time - now) if now < exp_time else "EXPIRED"
        
        return result
    except Exception as e:
        return {"error": f"Failed to analyze token: {e}"}


def load_web_token():
    """Try to load a web token from saved file with analysis"""
    try:
        if os.path.exists("web_token.json"):
            with open("web_token.json", "r") as f:
                data = json.load(f)
                token = data.get("token")
                
                if token:
                    # Analyze token to provide useful info
                    analysis = analyze_jwt_token(token)
                    if "expires_at" in analysis:
                        if analysis["is_expired"]:
                            print(f"⚠️  Found token but it expired at {analysis['expires_at']}")
                            return None  # Don't return expired tokens
                        else:
                            print(f"✅ Found valid token, expires: {analysis['expires_at']}")
                            print(f"   Time remaining: {analysis['time_remaining']}")
                    
                return token
    except Exception as e:
        print(f"⚠️  Error loading web token: {e}")
    return None


def create_spond_session(username: str, password: str, force_login: bool = False) -> spond.Spond:
    """
    Create a Spond session using the best available authentication method.
    
    Priority:
    1. Use saved web token if available (STRONGLY PREFERRED to avoid lockouts)
    2. Only attempt fresh login if explicitly requested and no token available
    
    Args:
        username: Spond username
        password: Spond password 
        force_login: If True, will attempt fresh login even without token (RISKY!)
    
    Returns:
        Spond session ready to use, or None if user aborts
    """
    # Always try to load a web token first
    web_token = load_web_token()
    
    if web_token:
        print(f"� Found saved web token (length: {len(web_token)})")
        print("✅ Using token to avoid login attempts and potential account lockouts")
        return TokenBasedSpond(username=username, password=password, token=web_token)
    
    # No token available - warn about risks
    print("⚠️  WARNING: No saved web token found!")
    print("🚨 Fresh login attempts may trigger account lockouts or rate limiting")
    print()
    print("🔧 RECOMMENDED SOLUTIONS:")
    print("1. [SAFEST] Run 'python web_token_extractor.py' to get a token from web login")
    print("2. [RISKY]  Proceed with fresh API login (may cause lockouts)")
    print("3. [SAFE]   Abort and get web token first")
    print()
    
    if not force_login:
        choice = input("Choose (1=extract token, 2=risky login, 3=abort): ").strip()
        
        if choice == "1":
            print("� Please run: python web_token_extractor.py")
            print("   Then re-run this script.")
            return None
        elif choice == "3" or choice == "":
            print("🚫 Aborted to prevent potential account lockout")
            return None
        elif choice != "2":
            print("❌ Invalid choice. Aborting for safety.")
            return None
    
    # User chose risky login or force_login=True
    print("⚠️  Proceeding with fresh login - BE CAREFUL!")
    print("🔄 This will attempt API login which may trigger 2FA or lockouts")
    
    confirm = input("Type 'YES' to confirm risky login: ").strip()
    if confirm != "YES":
        print("🚫 Login cancelled for safety")
        return None
        
    print("🚨 Starting risky fresh login...")
    return InteractiveSpond(username=username, password=password)