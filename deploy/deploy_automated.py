#!/usr/bin/env python3
"""
Prometheus V7 - Automated VPS Deploy Script
Hostinger VPS - AlmaLinux 9
"""

import os
import sys
import time
import paramiko
from pathlib import Path

# Configuration from environment variables
VPS_CONFIG = {
    'host': os.environ['VPS_HOST'],
    'port': int(os.environ.get('VPS_PORT', 22)),
    'username': os.environ.get('VPS_USER', 'root'),
    'password': os.environ['VPS_PASSWORD'],
    'domain': os.environ.get('VPS_DOMAIN', 'your-domain.com')
}

APP_DIR = '/opt/prometheus/app'
REPO_URL = 'https://github.com/Finish-Him/prometheus-v7.1.git'

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, total_steps, message):
    print(f"\n{Colors.YELLOW}[{step_num}/{total_steps}] {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def execute_ssh_command(ssh, command, show_output=True):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if show_output and output:
        print(output)
    if exit_status != 0:
        if error:
            print_error(f"Command failed: {error}")
        return False, error
    return True, output

def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        return True
    except Exception as e:
        print_error(f"Failed to upload {local_path}: {e}")
        return False

def main():
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("🔥 Prometheus V7 - Automated VPS Deploy")
    print("=" * 60)
    print(f"{Colors.ENDC}")

    print_step(1, 6, "Connecting to VPS...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=VPS_CONFIG['host'],
            port=VPS_CONFIG['port'],
            username=VPS_CONFIG['username'],
            password=VPS_CONFIG['password'],
            timeout=30
        )
        print_success(f"Connected to {VPS_CONFIG['host']}")
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        sys.exit(1)

    sftp = ssh.open_sftp()

    print_step(2, 6, "Uploading setup script...")
    setup_script = Path(__file__).parent / "setup_vps.sh"
    if setup_script.exists():
        upload_file(sftp, str(setup_script), "/tmp/setup_vps.sh")
        execute_ssh_command(ssh, "chmod +x /tmp/setup_vps.sh")
        print_success("Setup script uploaded")
    else:
        print_error("setup_vps.sh not found")
        sys.exit(1)

    print_step(3, 6, "Running setup script...")
    success, output = execute_ssh_command(ssh, f"bash /tmp/setup_vps.sh {REPO_URL} {APP_DIR}")
    if not success:
        print_error("Setup script failed")
        sys.exit(1)
    print_success("Setup complete")

    print_step(4, 6, "Uploading environment variables...")
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        upload_file(sftp, str(env_file), f"{APP_DIR}/.env")
        execute_ssh_command(ssh, f"chmod 600 {APP_DIR}/.env")
        print_success(".env uploaded")
    else:
        print_info(".env not found locally, skipping")

    print_step(5, 6, "Starting application...")
    execute_ssh_command(ssh, "systemctl restart prometheus")
    time.sleep(5)
    success, output = execute_ssh_command(ssh, "systemctl is-active prometheus")
    if 'active' in output:
        print_success("Application started")
    else:
        print_error("Application failed to start")
        execute_ssh_command(ssh, "journalctl -u prometheus -n 30 --no-pager")

    print_step(6, 6, "Verifying deployment...")
    success, output = execute_ssh_command(ssh, "curl -s http://localhost:8501 | head -3")
    if output:
        print_success("Application is responding")
    else:
        print_info("Application not yet responding (may need more time)")

    sftp.close()
    ssh.close()

    print(f"\n{Colors.GREEN}{Colors.BOLD}")
    print("=" * 60)
    print("🎉 Deployment Complete!")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    print(f"  🌐 http://{VPS_CONFIG['domain']}")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyError as e:
        print(f"❌ Missing required environment variable: {e}")
        print("Set VPS_HOST, VPS_PASSWORD (and optionally VPS_USER, VPS_PORT, VPS_DOMAIN) before running.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)