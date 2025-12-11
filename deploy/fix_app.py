#!/usr/bin/env python3
"""
Fix blank screen issue by deploying working app.py
"""

import paramiko
import sys
from pathlib import Path

VPS_CONFIG = {
    'host': '72.62.9.90',
    'port': 22,
    'username': 'root',
    'password': 'Moises@24512987'
}

def execute_command(ssh, command):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("🔧 Fixing blank screen issue...")
    print("="*60)
    
    # Connect to VPS
    print("\n1. Connecting to VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=VPS_CONFIG['host'],
        port=VPS_CONFIG['port'],
        username=VPS_CONFIG['username'],
        password=VPS_CONFIG['password']
    )
    print("✅ Connected")
    
    # Backup current app.py
    print("\n2. Backing up current app.py...")
    execute_command(ssh, "cp /opt/prometheus/app/app.py /opt/prometheus/app/app.py.broken")
    print("✅ Backup created: app.py.broken")
    
    # Upload working app.py
    print("\n3. Uploading working app.py...")
    sftp = ssh.open_sftp()
    local_app = Path(__file__).parent.parent / "app.py"
    
    if local_app.exists():
        sftp.put(str(local_app), "/opt/prometheus/app/app.py")
        print("✅ Working app.py uploaded")
    else:
        print("❌ Local app.py not found")
        sys.exit(1)
    
    # Set correct permissions
    execute_command(ssh, "chown prometheus:prometheus /opt/prometheus/app/app.py")
    
    # Restart service
    print("\n4. Restarting Prometheus service...")
    execute_command(ssh, "systemctl restart prometheus")
    print("✅ Service restarted")
    
    # Wait a bit for service to start
    import time
    print("\n5. Waiting for service to start...")
    time.sleep(5)
    
    # Check service status
    print("\n6. Checking service status...")
    status, output, error = execute_command(ssh, "systemctl is-active prometheus")
    if 'active' in output:
        print("✅ Service is active")
    else:
        print("❌ Service failed to start")
        status, output, error = execute_command(ssh, "journalctl -u prometheus -n 20 --no-pager")
        print(output)
    
    # Test application
    print("\n7. Testing application...")
    status, output, error = execute_command(ssh, "curl -s http://localhost:8501 | head -5")
    if 'DOCTYPE html' in output or 'Streamlit' in output:
        print("✅ Application is responding")
    else:
        print("⚠️  Application may not be fully loaded yet")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "="*60)
    print("🎉 Fix applied!")
    print("="*60)
    print("\nTest the application:")
    print("  - VPS: https://prometheus.mscconsultoriarj.com.br")
    print("  - Streamlit Cloud: Push to GitHub to update")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
