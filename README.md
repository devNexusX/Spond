# Spond Toolkit - Enhanced Python Scripts

An enhanced toolkit for working with the Spond API, featuring improved authentication handling, 2FA support, and web token management.

## 🔥 Key Features

- **🛡️ Safe Authentication**: Prioritizes web tokens to avoid account lockouts
- **📱 2FA Support**: Interactive SMS verification when needed
- **🔄 DRY Architecture**: Shared authentication helpers across all scripts
- **⚡ Web Token Extraction**: Extract long-lived tokens from browser sessions
- **📊 Multiple Export Formats**: Groups and attendance data

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/your-username/spond-toolkit.git
cd spond-toolkit
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy sample config
cp config.py.sample config.py

# Edit with your credentials
# Note: Username/password only used as fallback - web tokens preferred
```

### 3. Get Web Token (Recommended)
```bash
# Extract token from web browser (safest method)
python web_token_extractor.py

# Follow the prompts to extract token from https://spond.com
```

### 4. Use Scripts
```bash
# Export all groups
python groups.py

# Export attendance data
python attendance.py --from 2025-01-01 --to 2025-12-31

# Include all member responses
python attendance.py --from 2025-01-01 -a
```

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [Authentication Guide](docs/AUTHENTICATION.md) - How to safely authenticate
- [Examples](docs/EXAMPLES.md) - Common usage patterns

## 🔒 Security Features

- **Web Token Priority**: Uses browser-extracted tokens to minimize API login attempts
- **Account Protection**: Warns about operations that could cause lockouts  
- **JWT Analysis**: Checks token expiry without API calls
- **Conservative Testing**: Minimal authentication attempts

## 📁 Output

Scripts create organized exports in the `./exports/` directory:
- **Groups**: JSON files with complete group data
- **Attendance**: CSV files with event attendance details

## 🤝 Contributing

This is a fork/enhancement of the original Spond project with added authentication safety and usability improvements. 

### What's New:
- Shared authentication module (`spond_auth_helpers.py`)
- Web token extraction tool
- Enhanced error handling and user guidance
- Account lockout protection
- JWT token analysis

## 📄 License

This project maintains the original license terms. See [LICENSE](LICENSE) for details.

## 🙏 Credits

Based on the original Spond project by [Olen](https://github.com/Olen/Spond).

Enhanced with:
- Improved authentication handling
- 2FA support 
- Web token management
- Better security practices