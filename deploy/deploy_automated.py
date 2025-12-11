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

# Configuration
VPS_CONFIG = {
    'host': '72.62.9.90',
    'port': 22,
    'username': 'root',
    'password': 'Moises@24512987',
    'domain': 'prometheus.mscconsultoriarj.com.br'
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
    """Print formatted step message"""
    print(f"\n{Colors.YELLOW}[{step_num}/{total_steps}] {message}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def execute_ssh_command(ssh, command, show_output=True):
    """Execute command via SSH and return output"""
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
    """Upload file via SFTP"""
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
    
    # Connect to VPS
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
    
    # Open SFTP session
    sftp = ssh.open_sftp()
    
    # Upload setup script
    print_step(2, 6, "Uploading setup script...")
    
    local_script = Path(__file__).parent / 'setup_vps.sh'
    if local_script.exists():
        if upload_file(sftp, str(local_script), '/root/setup_vps.sh'):
            print_success("Setup script uploaded")
            execute_ssh_command(ssh, "chmod +x /root/setup_vps.sh", show_output=False)
        else:
            print_error("Failed to upload setup script")
            sys.exit(1)
    else:
        print_error(f"Setup script not found: {local_script}")
        sys.exit(1)
    
    # Execute setup script
    print_step(3, 6, "Executing setup on VPS (this may take 5-10 minutes)...")
    print_info("Installing dependencies, cloning repository, configuring services...")
    
    success, output = execute_ssh_command(ssh, "/root/setup_vps.sh", show_output=True)
    
    if success:
        print_success("Setup completed successfully")
    else:
        print_error("Setup script failed")
        print_info("Check logs on VPS: journalctl -u prometheus -f")
    
    # Upload .env file
    print_step(4, 6, "Uploading environment variables...")
    
    local_env = Path(__file__).parent.parent / '.env.production'
    if local_env.exists():
        if upload_file(sftp, str(local_env), f'{APP_DIR}/.env'):
            print_success("Environment variables uploaded")
            # Set correct permissions
            execute_ssh_command(ssh, f"chown prometheus:prometheus {APP_DIR}/.env", show_output=False)
            execute_ssh_command(ssh, f"chmod 600 {APP_DIR}/.env", show_output=False)
        else:
            print_error("Failed to upload .env file")
    else:
        print_error(f".env.production not found at {local_env}")
        print_info("You'll need to manually create .env on the VPS")
    
    # Restart service
    print_step(5, 6, "Restarting Prometheus service...")
    
    execute_ssh_command(ssh, "systemctl restart prometheus", show_output=False)
    time.sleep(3)
    
    success, output = execute_ssh_command(ssh, "systemctl is-active prometheus", show_output=False)
    
    if success and 'active' in output:
        print_success("Prometheus service is running")
    else:
        print_error("Prometheus service failed to start")
        print_info("Check logs: journalctl -u prometheus -n 50")
    
    # Verify deployment
    print_step(6, 6, "Verifying deployment...")
    
    success, output = execute_ssh_command(ssh, f"curl -s http://localhost:8501/health || echo 'Health check failed'", show_output=False)
    
    if 'OK' in output or success:
        print_success("Application is responding")
    else:
        print_error("Application health check failed")
    
    # Close connections
    sftp.close()
    ssh.close()
    
    # Final summary
    print(f"\n{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("🎉 Deploy Complete!")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    print(f"\n📍 Application URL: {Colors.CYAN}http://{VPS_CONFIG['domain']}{Colors.ENDC}")
    print(f"📍 Server IP: {Colors.CYAN}{VPS_CONFIG['host']}{Colors.ENDC}")
    print(f"\n{Colors.YELLOW}Next Steps:{Colors.ENDC}")
    print(f"  1. Test: curl http://{VPS_CONFIG['domain']}/health")
    print(f"  2. Setup SSL: ssh root@{VPS_CONFIG['host']} 'certbot --nginx -d {VPS_CONFIG['domain']}'")
    print(f"  3. Monitor: ssh root@{VPS_CONFIG['host']} 'journalctl -u prometheus -f'")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Deploy interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
