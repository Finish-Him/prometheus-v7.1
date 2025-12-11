#!/usr/bin/env python3
"""
Check application logs on VPS to diagnose blank screen issue
"""

import paramiko
import sys

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
    print("🔍 Checking Prometheus application logs...\n")
    
    # Connect to VPS
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=VPS_CONFIG['host'],
        port=VPS_CONFIG['port'],
        username=VPS_CONFIG['username'],
        password=VPS_CONFIG['password']
    )
    
    # Check service status
    print("1. Service Status:")
    print("="*60)
    status, output, error = execute_command(ssh, "systemctl status prometheus --no-pager -l")
    print(output)
    
    # Check recent logs
    print("\n2. Recent Logs (last 50 lines):")
    print("="*60)
    status, output, error = execute_command(ssh, "journalctl -u prometheus -n 50 --no-pager")
    print(output)
    
    # Check error logs
    print("\n3. Error Logs:")
    print("="*60)
    status, output, error = execute_command(ssh, "tail -50 /opt/prometheus/logs/prometheus-error.log 2>/dev/null || echo 'No error log file'")
    print(output)
    
    # Check if app.py exists and is correct
    print("\n4. Checking app.py:")
    print("="*60)
    status, output, error = execute_command(ssh, "ls -lh /opt/prometheus/app/app.py")
    print(output)
    
    # Check if main() is being called
    print("\n5. Checking if main() is called in app.py:")
    print("="*60)
    status, output, error = execute_command(ssh, "tail -5 /opt/prometheus/app/app.py")
    print(output)
    
    # Test Streamlit directly
    print("\n6. Testing Streamlit response:")
    print("="*60)
    status, output, error = execute_command(ssh, "curl -s http://localhost:8501 | head -20")
    print(output if output else "No response")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("Diagnosis complete!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
