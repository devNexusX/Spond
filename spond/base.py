from abc import ABC
from typing import Callable

import aiohttp

from spond import AuthenticationError


class _SpondBase(ABC):
    def __init__(self, username: str, password: str, api_url: str) -> None:
        self.username = username
        self.password = password
        self.api_url = api_url
        self.clientsession = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())
        self.token = None

    @property
    def auth_headers(self) -> dict:
        return {
            "content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    @staticmethod
    def require_authentication(func: Callable):
        async def wrapper(self, *args, **kwargs):
            if not self.token:
                try:
                    await self.login()
                except AuthenticationError as e:
                    await self.clientsession.close()
                    raise e
            return await func(self, *args, **kwargs)

        return wrapper

    async def login(self) -> None:
        login_url = f"{self.api_url}login"
        data = {"email": self.username, "password": self.password}
        async with self.clientsession.post(login_url, json=data) as r:
            login_result = await r.json()
            self.token = login_result.get("loginToken")
            
            # Check if 2FA is required
            if self.token is None and "token" in login_result and "phoneNumber" in login_result:
                print(f"🔄 2FA detected. Full response: {login_result}")
                # Try using the token directly first
                temp_token = login_result.get("token")
                if temp_token:
                    print("🧪 Attempting to use the returned token directly...")
                    self.token = temp_token
                    # Test if this token works by making a simple API call
                    if await self._test_token():
                        print("✅ Token works directly - 2FA not needed!")
                        return
                    else:
                        print("❌ Token doesn't work directly - need SMS verification")
                        self.token = None  # Reset token
                        
                # 2FA is required, need to verify with SMS code
                await self._handle_2fa(login_result)
            elif self.token is None:
                err_msg = f"Login failed. Response received: {login_result}"
                raise AuthenticationError(err_msg)

    async def _test_token(self) -> bool:
        """Test if the current token works by making a simple API call"""
        try:
            url = f"{self.api_url}groups/"
            async with self.clientsession.get(url, headers=self.auth_headers) as r:
                return r.status == 200
        except:
            return False

    async def _handle_2fa(self, login_result: dict) -> None:
        """Handle 2FA authentication flow"""
        temp_token = login_result.get("token")
        phone_number = login_result.get("phoneNumber", "")
        
        if not temp_token:
            raise AuthenticationError("2FA token missing from login response")
        
        # Get SMS code from user (this will be overridden in subclasses)
        sms_code = await self._get_2fa_code(phone_number)
        
        # Submit the 2FA code
        await self._submit_2fa_code(temp_token, sms_code)

    async def _get_2fa_code(self, phone_number: str) -> str:
        """Get 2FA code from user. This method should be overridden in subclasses."""
        raise AuthenticationError(f"2FA required for phone number {phone_number}. Please implement _get_2fa_code method.")

    async def _submit_2fa_code(self, temp_token: str, sms_code: str) -> None:
        """Submit 2FA code to complete authentication"""
        login_url = f"{self.api_url}login"
        
        # Try different variations of the login request with 2FA
        variations = [
            {"email": self.username, "password": self.password, "token": temp_token, "smsCode": sms_code},
            {"email": self.username, "password": self.password, "token": temp_token, "code": sms_code},
            {"email": self.username, "password": self.password, "sms": sms_code, "token": temp_token},
            {"token": temp_token, "smsCode": sms_code, "email": self.username, "password": self.password},
            {"token": temp_token, "code": sms_code, "email": self.username, "password": self.password}
        ]
        
        for i, data in enumerate(variations, 1):
            try:
                async with self.clientsession.post(login_url, json=data) as r:
                    verify_result = await r.json()
                    print(f"Variation {i} response: {verify_result}")
                    
                    self.token = verify_result.get("loginToken")
                    if self.token is not None:
                        print(f"✅ 2FA successful with variation {i}!")
                        return  # Success!
            except Exception as e:
                print(f"Variation {i} error: {e}")
        
        # Try different endpoints if login variations don't work
        possible_endpoints = [
            "login/verify",
            "login/sms", 
            "auth/verify",
            "auth/sms",
            "verify",
            "sms"
        ]
        
        for endpoint in possible_endpoints:
            verify_url = f"{self.api_url}{endpoint}"
            data = {"token": temp_token, "code": sms_code}
            
            try:
                async with self.clientsession.post(verify_url, json=data) as r:
                    if r.status == 404:
                        continue  # Try next endpoint
                        
                    verify_result = await r.json()
                    print(f"Endpoint {endpoint} response: {verify_result}")
                    
                    self.token = verify_result.get("loginToken")
                    if self.token is not None:
                        print(f"✅ 2FA successful with endpoint {endpoint}!")
                        return  # Success!
            except Exception as e:
                if "404" not in str(e):
                    print(f"Endpoint {endpoint} error: {e}")
                continue
        
        # If we get here, none of the approaches worked
        raise AuthenticationError("Could not complete 2FA verification. All approaches failed.")
