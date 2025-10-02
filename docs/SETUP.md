# Setup Guide

## Prerequisites

- Python 3.7 or higher
- Valid Spond account
- Internet connection

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/spond-toolkit.git
cd spond-toolkit
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials
```bash
# Copy the sample configuration
cp config.py.sample config.py

# Edit config.py with your Spond credentials
# Note: These are only used as fallback - web tokens are preferred
```

### 4. Set Up Authentication (Choose One)

#### Option A: Web Token (Recommended - Safest)
```bash
python web_token_extractor.py
```
Follow the interactive prompts to extract a token from your browser.

#### Option B: Direct API (Risky - May Cause Lockouts)
The scripts will prompt for 2FA if no web token is available.

## Verification

Test your setup:
```bash
# Should show available groups without 2FA
python groups.py

# Should show help without errors  
python attendance.py --help
```

## Troubleshooting

### Common Issues

**"No valid authentication token"**
- Solution: Run `python web_token_extractor.py` to get a web token

**"Token expired"**  
- Solution: Extract a fresh token from your browser

**"Account locked" / Rate limiting**
- Solution: Wait and use web tokens instead of API login

**Import errors**
- Solution: Ensure you're in the project directory and dependencies are installed

### Getting Help

1. Check this documentation
2. Review the authentication guide
3. Check the examples
4. Open an issue on GitHub