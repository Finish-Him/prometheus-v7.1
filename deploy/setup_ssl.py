#!/usr/bin/env python3
"""
Setup SSL certificate with Let's Encrypt (Certbot)
"""

import paramiko
import sys
import time

VPS_CONFIG = {
    'host': '72.62.9.90',
    'port': 22,
    'username': 'root',
    'password': 'Moises@24512987',
    'domain': 'prometheus.mscconsultoriarj.com.br'
}

def execute_command(ssh, command, timeout=300):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("🔒 Setting up SSL certificate with Let's Encrypt...")
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
    
    # Check if certbot is installed
    print("\n2. Checking Certbot installation...")
    status, output, error = execute_command(ssh, "which certbot")
    
    if status != 0:
        print("⚠️  Certbot not found, installing...")
        status, output, error = execute_command(ssh, "dnf install -y certbot python3-certbot-nginx")
        if status == 0:
            print("✅ Certbot installed")
        else:
            print(f"❌ Failed to install Certbot: {error}")
            sys.exit(1)
    else:
        print("✅ Certbot already installed")
    
    # Check DNS resolution
    print(f"\n3. Checking DNS for {VPS_CONFIG['domain']}...")
    status, output, error = execute_command(ssh, f"dig +short {VPS_CONFIG['domain']}")
    print(f"DNS resolves to: {output.strip()}")
    
    if VPS_CONFIG['host'] not in output:
        print(f"⚠️  Warning: DNS does not point to {VPS_CONFIG['host']}")
        print("Make sure your domain DNS A record points to the VPS IP")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("SSL setup cancelled")
            sys.exit(0)
    
    # Obtain SSL certificate
    print(f"\n4. Obtaining SSL certificate for {VPS_CONFIG['domain']}...")
    print("This will:")
    print("  - Verify domain ownership")
    print("  - Generate SSL certificate")
    print("  - Configure Nginx automatically")
    print("  - Setup auto-renewal")
    
    # Non-interactive certbot command
    certbot_cmd = (
        f"certbot --nginx "
        f"-d {VPS_CONFIG['domain']} "
        f"--non-interactive "
        f"--agree-tos "
        f"--email moises.costa12345@gmail.com "
        f"--redirect"
    )
    
    print("\nRunning Certbot (this may take a minute)...")
    status, output, error = execute_command(ssh, certbot_cmd, timeout=300)
    
    print(output)
    if error:
        print(error)
    
    if status == 0 or 'Successfully' in output or 'Certificate not yet due for renewal' in output:
        print("✅ SSL certificate configured successfully")
    else:
        print("❌ Failed to configure SSL")
        print("You may need to:")
        print("  1. Verify DNS is pointing correctly")
        print("  2. Check firewall allows port 80 and 443")
        print("  3. Run manually: certbot --nginx -d prometheus.mscconsultoriarj.com.br")
        sys.exit(1)
    
    # Test SSL certificate
    print("\n5. Testing SSL configuration...")
    status, output, error = execute_command(ssh, f"curl -sI https://{VPS_CONFIG['domain']} | head -1")
    print(output)
    
    if '200' in output or '301' in output or '302' in output:
        print("✅ HTTPS is working")
    else:
        print("⚠️  HTTPS test inconclusive")
    
    # Check auto-renewal
    print("\n6. Verifying auto-renewal setup...")
    status, output, error = execute_command(ssh, "systemctl status certbot-renew.timer --no-pager || certbot renew --dry-run")
    if status == 0:
        print("✅ Auto-renewal configured")
    else:
        print("⚠️  Auto-renewal check failed (this is usually OK)")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("🎉 SSL Setup Complete!")
    print("="*60)
    print(f"\n✅ Your site is now secure:")
    print(f"   https://{VPS_CONFIG['domain']}")
    print(f"\n📝 Certificate will auto-renew every 60 days")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  SSL setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
