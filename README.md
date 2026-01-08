# OpenVPN Auto-Login with PIN + TOTP (Node.js)

Automated OpenVPN connection using PIN + TOTP authentication. Connects with a single command and disconnects cleanly.

## Prerequisites

- **Node.js**: Ensure Node.js is installed.
- **OpenVPN**: Install via Homebrew.

```bash
brew install openvpn
```

## Installation

1.  Clone this repository.
2.  Install dependencies:

```bash
npm install
```

3.  (Optional) Link globally:

```bash
npm link
```
This allows you to run `vpn-up` and `vpn-down` from anywhere.

## Setup

### 1. Store Credentials in macOS Keychain

You need to store two items in your Keychain:
- Your **PIN** (static password prefix)
- Your **TOTP secret** (base32 secret for generating time-based codes)

Run these commands (you'll be prompted to enter each value securely):

```bash
# Store PIN
security add-generic-password -a "$USER" -s "vpn_pin" -w

# Store TOTP secret (paste your base32 secret when prompted)
security add-generic-password -a "$USER" -s "vpn_totp_secret" -w
```

**Important:** When prompted, paste your PIN or TOTP secret and press Enter. The `-w` flag ensures the input is hidden.

To update existing entries:
```bash
security delete-generic-password -a "$USER" -s "vpn_pin" 2>/dev/null
security add-generic-password -a "$USER" -s "vpn_pin" -w
```

### 2. Configure Your OpenVPN Profile Path

Create a `.env` file in the project root to store the path to your `.ovpn` configuration file.

1.  Copy the example file:
    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` and set `VPN_CONFIG` (and optionally `VPN_USER` if it differs from your system username):
    ```bash
    VPN_CONFIG=/path/to/your/config.ovpn
    VPN_USER=your_username
    ```

Alternatively, you can still export the environment variable `VPN_CONFIG` or pass the path as an argument.

## Usage

### Connect to VPN

Recommended way:
```bash
npm run vpn-up
```

If `npm link` was used:
```bash
vpn-up
```

Otherwise:
```bash
node src/vpn-up
```

Or with explicit config path:
```bash
npm run vpn-up -- /path/to/config.ovpn
```

The script will:
...
### Disconnect from VPN

Recommended way:
```bash
npm run vpn-down
```

If `npm link` was used:
```bash
vpn-down
```

Otherwise:
```bash
node src/vpn-down
```

This will:
1. Stop the OpenVPN process
2. Clean up the PID file
3. Remove temporary authentication file

## How It Works

1. **Authentication**: The script generates the password as `PIN + TOTP` where:
   - PIN is retrieved from Keychain (`vpn_pin`)
   - TOTP is computed using the Node.js `otplib` library from the secret stored in Keychain (`vpn_totp_secret`)

2. **OpenVPN Launch**: A temporary file is created with the username (ignored) and password, then OpenVPN is started with `--auth-user-pass` pointing to this file.

3. **Process Management**: The OpenVPN PID is saved to `~/.vpn.pid` for easy disconnection.

## Troubleshooting

### Time Synchronization

TOTP codes require accurate system time. If you get authentication errors:
```bash
# Check system time
date

# Sync time if needed (macOS usually handles this automatically)
sudo sntp -sS time.apple.com
```

### View Logs

Connection logs are saved to `~/.vpn.log`:
```bash
tail -f ~/.vpn.log
```

### Keychain Access

If you see Keychain access errors, make sure:
- The Keychain items exist (check with `security find-generic-password -a "$USER" -s "vpn_pin"`)
- You've granted Terminal/Cursor access to your Keychain (macOS will prompt you)

## Security Notes

- Secrets are stored in macOS Keychain (encrypted by the OS)
- Temporary password files are created with restricted permissions (0600) and cleaned up automatically
- No secrets appear in command-line history or process lists