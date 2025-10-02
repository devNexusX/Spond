"""
Script to help extract authentication token from Spond web login.

Instructions:
1. Run this script
2. Open your browser and log into Spond web interface
3. Open browser developer tools (F12)
4. Go to Network tab
5. Make any request (refresh page or click something)
6. Look for requests to api.spond.com
7. Check the Authorization header - it will contain "Bearer <token>"
8. Copy that token and use it in your config

Alternatively, you can check Local Storage or Session Storage in the browser
for stored tokens.
"""

import json
import os
from datetime import datetime

def save_token_to_config(token: str):
    """Save the extracted token to a config file"""
    config_data = {
        "token": token,
        "extracted_at": datetime.now().isoformat(),
        "note": "Token extracted from web login session"
    }
    
    with open("web_token.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    print(f"✅ Token saved to web_token.json")
    print(f"Token length: {len(token)} characters")
    print(f"Token preview: {token[:50]}...")

def load_saved_token():
    """Load a previously saved token"""
    if os.path.exists("web_token.json"):
        with open("web_token.json", "r") as f:
            data = json.load(f)
        return data.get("token")
    return None

def create_token_based_spond_class():
    """Create a modified Spond class that uses a pre-existing token"""
    code = '''
# Add this to your script to use a saved token:

from spond import spond
import json

class TokenBasedSpond(spond.Spond):
    """Spond class that uses a pre-existing token instead of login"""
    
    def __init__(self, username: str, password: str, token: str = None):
        super().__init__(username, password)
        if token:
            self.token = token
            print(f"✅ Using pre-existing token (length: {len(token)})")
    
    async def login(self) -> None:
        """Override login to use existing token or fall back to normal login"""
        if self.token:
            # Test if the existing token works
            if await self._test_token():
                print("✅ Existing token is valid - skipping login")
                return
            else:
                print("❌ Existing token expired - falling back to normal login")
                self.token = None
        
        # Fall back to normal login if no token or token expired
        await super().login()
    
    async def _test_token(self) -> bool:
        """Test if the current token works"""
        try:
            url = f"{self.api_url}groups/"
            async with self.clientsession.get(url, headers=self.auth_headers) as r:
                return r.status == 200
        except:
            return False

# Usage example:
# Load token from saved file
with open("web_token.json", "r") as f:
    token_data = json.load(f)
    saved_token = token_data["token"]

# Use the token-based Spond class
s = TokenBasedSpond(username="your_username", password="your_password", token=saved_token)
'''
    
    with open("token_based_spond_example.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    print("\n📝 Created token_based_spond_example.py with usage example")

def main():
    print("🔍 Spond Web Token Extractor")
    print("=" * 50)
    
    print("\n📋 Instructions to extract token from web login:")
    print("1. Open https://spond.com and log in")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Network tab")
    print("4. Refresh the page or navigate somewhere")
    print("5. Find requests to 'api.spond.com'")
    print("6. Look for 'Authorization: Bearer <long_token>' in request headers")
    print("7. Copy the token (without 'Bearer ' prefix)")
    
    print("\n🔧 Alternative methods:")
    print("- Check Application -> Local Storage -> spond.com in Dev Tools")
    print("- Check Application -> Session Storage -> spond.com in Dev Tools")
    print("- Look for keys like 'authToken', 'loginToken', 'token', etc.")
    
    # Check if we have a saved token
    saved_token = load_saved_token()
    if saved_token:
        print(f"\n💾 Found previously saved token (length: {len(saved_token)})")
        use_saved = input("Use saved token? (y/n): ").strip().lower()
        if use_saved == 'y':
            print("✅ Using saved token")
            create_token_based_spond_class()
            return
    
    # Get new token from user
    print("\n🔑 Enter the token you extracted:")
    token = input("Token: ").strip()
    
    if token:
        if len(token) < 50:
            print("⚠️  Token seems too short. Make sure you copied the full token.")
        else:
            save_token_to_config(token)
            create_token_based_spond_class()
            print("\n🎉 Setup complete! Check the generated files.")
    else:
        print("❌ No token provided")

if __name__ == "__main__":
    main()