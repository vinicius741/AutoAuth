# AutoAuth - Automated VPN Connection with PIN + TOTP

Automated OpenVPN connection using PIN + TOTP authentication. Connects with a single command and disconnects cleanly with real-time status monitoring.

## Features

 - **One-Command Connection**: Connect to VPN with automatic PIN + TOTP authentication
 - **Real-Time Status**: Monitor connection progress with colored output
 - **Environment-Based Credentials**: Store PIN and TOTP secret in .env file
 - **No Sudo Required**: Runs without sudo by default
- **Process Management**: Graceful shutdown with PID tracking
- **Comprehensive Logging**: All logs stored in project directory (`logs/`)
- **Status Monitoring**: Check connection state, duration, and IP address
- **Flexible Log Viewing**: Follow logs in real-time or view last N lines

## Prerequisites

- **Python 3.6+**: Ensure Python 3 is installed
- **OpenVPN**: Install via Homebrew

```bash
brew install openvpn
```

## Installation

1. **Clone this repository**

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and set your VPN configuration:

```bash
VPN_CONFIG=/path/to/your/config.ovpn
VPN_USERNAME=your_username

# Authentication credentials
VPN_PIN=your_pin
VPN_TOTP_SECRET=your_totp_secret
```

Optional settings:
```bash
VPN_PID_FILE=.vpn.pid  # Default: .vpn.pid
VPN_LOG_DIR=logs/       # Default: logs/
```

**Security Note**: The `.env` file contains sensitive credentials. Never commit this file to version control. It's included in `.gitignore`.

## Usage

### Connect to VPN

```bash
# Connect using config from .env
./vpn-connect

# Connect with specific config file
./vpn-connect /path/to/config.ovpn
```

The script will:
1. Read PIN and TOTP secret from .env file
2. Generate TOTP code automatically
3. Combine PIN + TOTP for authentication
4. Start OpenVPN and monitor connection
5. Display real-time connection progress
6. Show success or error messages

### Disconnect from VPN

```bash
./vpn-disconnect
```

This will:
1. Gracefully terminate OpenVPN process
2. Clean up PID files
3. Report disconnection status

### Check VPN Status

```bash
./vpn-status
```

Displays:
- Connection state (Connected/Disconnected)
- Process ID
- VPN IP address
- Connection duration
- Recent log entries
- Log file location

### View Logs

```bash
# View last 50 lines (default)
./vpn-logs

# View last 100 lines
./vpn-logs --tail 100

# Follow logs in real-time (tail -f)
./vpn-logs --follow
# or
./vpn-logs -f

# Filter by log level
./vpn-logs --level ERROR
./vpn-logs --level SUCCESS
```

## How It Works

1. **Authentication**: The script generates the password as `PIN + TOTP` where:
   - PIN is read from `.env` file (`VPN_PIN`)
   - TOTP is computed using the `pyotp` library from the secret in `.env` file (`VPN_TOTP_SECRET`)

2. **OpenVPN Launch**: A temporary file is created with the username and password, then OpenVPN is started with `--auth-user-pass` pointing to this file

3. **Process Management**: The OpenVPN PID is saved to `.vpn.pid` for easy disconnection and status tracking

4. **Logging**: All OpenVPN logs are stored in `logs/vpn.log`, and application logs in `logs/connection.log`

## Troubleshooting

### Time Synchronization

TOTP codes require accurate system time. If you get authentication errors:

```bash
# Check system time
date

# Sync time if needed (macOS usually handles this automatically)
sudo sntp -sS time.apple.com
```

### OpenVPN Not Found

If you see "OpenVPN not found" errors:

```bash
# Check if openvpn is installed
which openvpn

# Install via Homebrew
brew install openvpn
```

### Credentials Not Found

If you see "Failed to retrieve PIN" or "Failed to retrieve TOTP secret" errors:

```bash
# Check that .env file exists
ls -la .env

# Verify .env file has required variables
cat .env

# Ensure .env file is properly formatted (no extra spaces around =)
```

Make sure you have these variables in your `.env` file:
- `VPN_PIN` - Your static PIN
- `VPN_TOTP_SECRET` - Your base32 TOTP secret

### Connection Timeouts

If connection times out:

1. Check logs for detailed error messages:
   ```bash
   ./vpn-logs
   ```

2. Verify your VPN config file is valid:
   ```bash
   openvpn --config /path/to/config.ovpn --test-config
   ```

3. Ensure your PIN and TOTP secret are correct:
   - Test TOTP generation with an authenticator app
   - Verify the base32 secret is correct

### Process Won't Stop

If OpenVPN won't stop:

```bash
# Try the disconnect script
./vpn-disconnect

# If that fails, manually kill the process
./vpn-disconnect

# Or use system tools
pkill openvpn
```

## Project Structure

```
autoauth/
├── vpn-connect          # Main connection script
├── vpn-disconnect       # Disconnect script
├── vpn-status           # Status checker
├── vpn-logs             # Log viewer
├── vpn_utils.py         # Shared utility functions
├── .env                 # Configuration (not in git)
├── .env.example         # Configuration template
├── .gitignore          # Git ignore rules
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── logs/               # Log directory (auto-created)
│   ├── vpn.log        # OpenVPN logs
│   └── connection.log # Application logs
└── .vpn.pid           # Process ID file (auto-created)
```

## Security Notes

- Secrets are stored in `.env` file (included in `.gitignore` - never commit this file)
- Temporary password files are created with restricted permissions (0600) and cleaned up automatically
- No secrets appear in command-line history or process lists
- All scripts are executable and have proper permissions
- Consider using environment variable managers (e.g., `direnv`, `envchain`) for added security

## Contributing

This is a personal project for automating VPN connections. Feel free to fork and modify for your own use.

## License

ISC
