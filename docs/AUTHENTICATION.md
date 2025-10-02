# Authentication Guide

## 🛡️ Overview

This toolkit provides multiple authentication methods with a focus on safety and avoiding account lockouts.

## 🏆 Recommended Method: Web Tokens

### Why Web Tokens?
- ✅ **No 2FA required** after initial web login
- ✅ **No API login attempts** - can't cause lockouts  
- ✅ **Long-lived** - work for extended periods
- ✅ **Safe** - extracted from your own browser session

### How to Get a Web Token

1. **Run the extractor**:
   ```bash
   python web_token_extractor.py
   ```

2. **Log into Spond in your browser**:
   - Go to https://spond.com
   - Log in normally (this may require 2FA)
   - Navigate around (click groups, events, etc.)

3. **Extract the token**:
   - Open browser Developer Tools (F12)
   - Go to Network tab
   - Refresh the page or click something
   - Find requests to `api.spond.com`
   - Look for `Authorization: Bearer <long_token>` in request headers
   - Copy just the token part (without "Bearer ")

4. **Save the token**:
   - Paste it into the extractor script
   - It will be saved to `web_token.json`

### Token Lifespan
- Tokens typically last for weeks or months
- The toolkit automatically detects expired tokens
- You'll get clear prompts to refresh when needed

## ⚠️ Alternative: Direct API Login

### When to Use
- Only when web token extraction fails
- Emergency access situations
- Testing/development

### Risks
- May trigger 2FA SMS every time
- Repeated attempts can cause account lockouts
- Rate limiting by Spond servers

### How It Works
1. Script detects no valid web token
2. Shows safety warnings and options
3. Requires explicit confirmation ("YES")
4. Attempts API login with 2FA handling

## 🔒 Security Features

### Automatic Protection
- **Token Analysis**: Checks JWT expiry without API calls
- **Conservative Testing**: Minimal validation requests
- **Clear Warnings**: Explicit risk notifications
- **User Confirmation**: No accidental risky operations

### Best Practices
1. **Use web tokens** whenever possible
2. **Refresh tokens** before they expire
3. **Avoid repeated API logins** in short periods
4. **Monitor for 401 errors** indicating token expiry

## 🔄 Authentication Flow

```
1. Check for saved web token
   ├─ Token exists & valid → ✅ Use token
   ├─ Token expired → ❌ Prompt for new token
   └─ No token → ⚠️ Show safety warnings
   
2. If no token available:
   ├─ Option 1: Extract from web (recommended)
   ├─ Option 2: Risky API login (requires confirmation)
   └─ Option 3: Abort (safest)

3. Token validation:
   ├─ One-time API test per session
   ├─ Cache result to avoid repeated calls
   └─ Clear feedback on success/failure
```

## 🆘 Troubleshooting

### "Token expired"
- **Cause**: JWT expiry time reached
- **Solution**: Extract fresh token from browser

### "No valid authentication token"
- **Cause**: No saved token or token invalid
- **Solution**: Run `python web_token_extractor.py`

### "Account temporarily locked"
- **Cause**: Too many API login attempts
- **Solution**: Wait and switch to web tokens

### "2FA required repeatedly"
- **Cause**: Using API login instead of web tokens
- **Solution**: Extract and use web token instead

## 📱 2FA Handling

When direct API login is used:
1. Script detects 2FA requirement
2. Shows phone number (masked)
3. Prompts for SMS code
4. Handles verification automatically
5. Warns about potential lockout risks

**Note**: 2FA is completely avoided when using web tokens!