#!/usr/bin/env python3
"""
Fix Nginx configuration and ensure it's running properly
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
    print("🔧 Fixing Nginx configuration...")
    
    # Connect to VPS
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=VPS_CONFIG['host'],
        port=VPS_CONFIG['port'],
        username=VPS_CONFIG['username'],
        password=VPS_CONFIG['password']
    )
    
    # Check Nginx status
    print("\n1. Checking Nginx status...")
    status, output, error = execute_command(ssh, "systemctl status nginx --no-pager")
    print(output)
    
    # Check if port 80 is available
    print("\n2. Checking port 80...")
    status, output, error = execute_command(ssh, "ss -tlnp | grep :80")
    print(output if output else "Port 80 is free")
    
    # Stop conflicting services (cPanel Apache might be using port 80)
    print("\n3. Checking for Apache/httpd...")
    status, output, error = execute_command(ssh, "systemctl status httpd --no-pager || echo 'httpd not running'")
    if 'active (running)' in output:
        print("⚠️  Apache is running on port 80, stopping it...")
        execute_command(ssh, "systemctl stop httpd")
        execute_command(ssh, "systemctl disable httpd")
        print("✅ Apache stopped")
    
    # Test Nginx configuration
    print("\n4. Testing Nginx configuration...")
    status, output, error = execute_command(ssh, "nginx -t")
    print(output + error)
    
    # Start Nginx
    print("\n5. Starting Nginx...")
    status, output, error = execute_command(ssh, "systemctl start nginx")
    if status == 0:
        print("✅ Nginx started successfully")
    else:
        print(f"❌ Failed to start Nginx: {error}")
    
    # Enable Nginx on boot
    execute_command(ssh, "systemctl enable nginx")
    
    # Check final status
    print("\n6. Final Nginx status...")
    status, output, error = execute_command(ssh, "systemctl is-active nginx")
    if 'active' in output:
        print("✅ Nginx is active and running")
    else:
        print(f"❌ Nginx is not running: {output}")
    
    # Test application access
    print("\n7. Testing application access...")
    status, output, error = execute_command(ssh, "curl -s http://localhost/health || echo 'Failed'")
    if 'OK' in output or status == 0:
        print("✅ Application accessible via Nginx")
    else:
        print(f"⚠️  Application not accessible: {output}")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("🎉 Nginx configuration fixed!")
    print("="*60)
    print("\nYou can now access the application at:")
    print("http://prometheus.mscconsultoriarj.com.br")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
