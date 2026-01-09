# AGENTS.md - AutoAuth VPN Automation

This file provides guidelines for agentic coding assistants working on this repository.

## Build/Lint/Test Commands

This project has no automated test suite. Manual testing is performed by:

```bash
# Install dependencies
pip3 install --break-system-packages -r requirements.txt

# Syntax check all Python files
python3 -m py_compile vpn-connect vpn-disconnect vpn-status vpn-logs vpn_utils.py

# Manual testing
./vpn-status                    # Check VPN status (should show DISCONNECTED)
./vpn-disconnect               # Test disconnect when not running
./vpn-connect /path/to/config.ovpn  # Test connection (requires valid config)
./vpn-logs --tail 10          # Test log viewer
./vpn-logs -f                 # Test log following (Ctrl+C to exit)
```

To test a single script: Execute it directly with `./script-name` or `python3 script-name`.

## Code Style Guidelines

### File Structure

- Executable scripts: No `.py` extension (e.g., `vpn-connect`, `vpn-status`)
- Library modules: `.py` extension (e.g., `vpn_utils.py`)
- All scripts must have executable shebang: `#!/usr/bin/env python3`
- All executable scripts must be marked as executable: `chmod +x script-name`

### Imports

Order: Standard library → Third-party → Local imports

```python
import os
import sys
import subprocess
import time

import pyotp
from dotenv import load_dotenv

from vpn_utils import (
    get_keychain_password,
    generate_totp,
    read_env_var
)
```

- Use separate lines for multiple imports from same module with parentheses
- Avoid wildcard imports (`from module import *`)

### Naming Conventions

- **Functions**: `snake_case` (e.g., `get_keychain_password`, `print_status`)
- **Variables**: `snake_case` (e.g., `vpn_config`, `auth_file`, `pid`)
- **Constants**: `UPPER_SNAKE_CASE` (not currently used, but prefer this pattern)
- **Files**: `snake_case` for modules, no extension for executable scripts

### Formatting

- Use 4-space indentation (Python PEP 8 standard)
- Maximum line length: ~100 characters
- Blank line between top-level functions
- No trailing whitespace
- Use f-strings for string formatting (Python 3.6+)

### Function Design

- Keep functions small and focused on single responsibility
- Use descriptive names that clearly indicate purpose
- Provide sensible defaults for optional parameters
- Return early for error conditions to reduce nesting

```python
def get_keychain_password(account, service):
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-a', account, '-s', service, '-w'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to retrieve {service} from Keychain: {e.stderr.strip()}")
```

### Error Handling

- Catch specific exceptions when possible (`subprocess.CalledProcessError`, `OSError`, `ValueError`)
- Re-raise with context using f-strings for debugging
- Use bare `except Exception` only for cleanup where errors should be ignored
- Log errors to both terminal (via `print_status()`) and file (via `log_message()`)

```python
# Good: Specific exception with context
try:
    subprocess.run(['command'], check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    print_status(f"Command failed: {e.stderr}", 'ERROR')
    sys.exit(1)

# Acceptable: Silent cleanup
def cleanup_auth_file(auth_file):
    try:
        if os.path.exists(auth_file):
            os.remove(auth_file)
    except Exception:
        pass  # Ignore cleanup errors
```

### Logging

Use the custom logging utilities from `vpn_utils`:

```python
from vpn_utils import get_connection_log_file, log_message

conn_log = get_connection_log_file()
log_message(conn_log, "Operation started", 'INFO')
log_message(conn_log, "Operation completed", 'SUCCESS')
log_message(conn_log, "Error occurred", 'ERROR')
```

Log levels: `INFO`, `SUCCESS`, `WARNING`, `ERROR`

For terminal output, use `print_status()` with colored output:

```python
def print_status(message, level='INFO'):
    level_colors = {
        'INFO': '\033[94m',
        'SUCCESS': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m'
    }
    color = level_colors.get(level, '')
    reset = '\033[0m'
    print(f"{color}[{level}]{reset} {message}", flush=True)
```

### Subprocess Usage

Always use explicit arguments for subprocess calls:

```python
result = subprocess.run(
    ['command', '--arg', 'value'],
    capture_output=True,
    text=True,
    check=True
)
# For commands that might fail:
result = subprocess.run(
    ['command'],
    capture_output=True,
    text=True,
    check=False
)
if result.returncode == 0:
    # Success handling
    pass
```

### File Operations

- Always use `with open()` context manager for file I/O
- Set secure permissions for sensitive files (e.g., auth files): `os.chmod(auth_file.name, 0o600)`
- Use `os.path.join()` for cross-platform path construction
- Use `os.path.abspath()` to resolve relative paths

```python
# Good: Context manager with secure permissions
auth_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.auth')
auth_file.write(f"{username}\n{password}\n")
auth_file.close()
os.chmod(auth_file.name, 0o600)

# Good: Safe file reading
with open(log_file, 'r') as f:
    content = f.read()
```

### Script Structure

All executable scripts must follow this pattern:

```python
#!/usr/bin/env python3

import os
import sys
import subprocess
from vpn_utils import ( ... )

def helper_function():
    # Helper functions
    pass

def main():
    # Main logic
    print_status("Starting...", 'INFO')
    
    try:
        # Main execution
        pass
    except KeyboardInterrupt:
        print_status("Interrupted by user", 'WARNING')
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", 'ERROR')
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### Exit Codes

- `sys.exit(0)` or implicit exit for success
- `sys.exit(1)` for errors and failures
- Always provide user feedback before exiting on errors

### Environment Variables

- Use `python-dotenv` to load `.env` file
- Access variables via `os.getenv()` or `read_env_var()` utility
- Default values should be provided in `.env.example`
- Never commit `.env` file to git

### Colored Terminal Output

Use ANSI escape codes for terminal colors:

- Blue/Info: `\033[94m`
- Green/Success: `\033[92m`
- Yellow/Warning: `\033[93m`
- Red/Error: `\033[91m`
- Cyan/Header: `\033[96m`
- Reset: `\033[0m`

### Security Best Practices

- Never log or print passwords, PINs, or TOTP codes
- Use macOS Keychain for credential storage via `security` command
- Set restrictive file permissions (0600) for temporary auth files
- Clean up temporary files immediately after use
- Avoid using `sudo` unless absolutely necessary

### macOS-Specific Notes

- Use `security` command for Keychain operations
- Use `pgrep` and `kill` for process management
- Use `ifconfig` for network interface information
- Use `ps` for process details (start time, etc.)

### Documentation

- Currently, functions do NOT use docstrings (this is acceptable for this project)
- All user-facing messages should be clear and actionable
- README.md should be updated for significant features or changes

### Testing Philosophy

- Test with valid and invalid inputs
- Test error paths (missing files, invalid credentials, etc.)
- Test cleanup on failures
- Verify log messages are written correctly
- Manual testing is acceptable; no automated test suite exists
