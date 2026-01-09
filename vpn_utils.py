import os
import subprocess
import time
from datetime import datetime
import pyotp
from dotenv import load_dotenv

load_dotenv()

def generate_totp(secret):
    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception as e:
        raise Exception(f"Failed to generate TOTP code: {str(e)}")

def read_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if value is None:
        if default is None:
            raise Exception(f"Environment variable {var_name} not set")
        return default
    return value

def read_pid_file():
    pid_file = read_env_var('VPN_PID_FILE', '.vpn.pid')
    if not os.path.exists(pid_file):
        return None
    with open(pid_file, 'r') as f:
        return f.read().strip()

def write_pid_file(pid):
    pid_file = read_env_var('VPN_PID_FILE', '.vpn.pid')
    with open(pid_file, 'w') as f:
        f.write(str(pid))

def is_process_running(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False

def get_vpn_ip():
    try:
        result = subprocess.run(
            ['ifconfig', 'tun0'],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'inet' and i + 1 < len(parts):
                        return parts[i + 1]
    except subprocess.CalledProcessError:
        pass
    return None

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def get_log_file():
    log_dir = read_env_var('VPN_LOG_DIR', 'logs/')
    return os.path.join(log_dir, 'vpn.log')

def get_connection_log_file():
    log_dir = read_env_var('VPN_LOG_DIR', 'logs/')
    return os.path.join(log_dir, 'connection.log')

def setup_logging(log_file):
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_file

def log_message(log_file, message, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)
    
    return log_entry.strip()

def cleanup_auth_file(auth_file):
    try:
        if os.path.exists(auth_file):
            os.remove(auth_file)
    except Exception:
        pass

def get_process_start_time(pid):
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'lstart='],
            capture_output=True,
            text=True,
            check=True
        )
        start_time_str = result.stdout.strip()
        if start_time_str:
            start_time = datetime.strptime(start_time_str, '%a %b %d %H:%M:%S %Y')
            return start_time
    except (subprocess.CalledProcessError, ValueError):
        pass
    return None
