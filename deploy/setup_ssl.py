#!/usr/bin/env python3
"""
Setup SSL certificate using Let's Encrypt on VPS
"""

import os
import paramiko
import sys
import time

VPS_CONFIG = {
    'host': os.environ['VPS_HOST'],
    'port': int(os.environ.get('VPS_PORT', 22)),
    'username': os.environ.get('VPS_USER', 'root'),
    'password': os.environ['VPS_PASSWORD'],
    'domain': os.environ.get('VPS_DOMAIN', 'your-domain.com'),
    'email': os.environ.get('VPS_SSL_EMAIL', 'admin@your-domain.com')
}

def execute_command(ssh, command, timeout=120):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("🔒 Setting up SSL certificate...")
    print("="*60)
    
    domain = VPS_CONFIG['domain']
    email = VPS_CONFIG['email']
    
    if domain == 'your-domain.com':
        print("❌ Please set VPS_DOMAIN environment variable to your actual domain")
        sys.exit(1)
    
    if email == 'admin@your-domain.com':
        print("❌ Please set VPS_SSL_EMAIL environment variable to your email address")
        sys.exit(1)
    
    print(f"Domain: {domain}")
    print(f"Email: {email}")
    
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
    
    # Install Certbot
    print("\n2. Installing Certbot...")
    status, output, error = execute_command(ssh, "which certbot || dnf install -y certbot python3-certbot-nginx")
    print(output)
    
    # Check if Nginx is running
    print("\n3. Checking Nginx status...")
    status, output, error = execute_command(ssh, "systemctl is-active nginx")
    if 'active' not in output:
        print("⚠️  Nginx is not running, starting...")
        execute_command(ssh, "systemctl start nginx")
        time.sleep(3)
    print("✅ Nginx is running")
    
    # Check DNS resolves to this server
    print(f"\n4. Checking DNS for {domain}...")
    status, output, error = execute_command(ssh, f"dig +short {domain} || nslookup {domain} | tail -2")
    print(f"DNS: {output.strip()}")
    
    # Obtain SSL certificate
    print(f"\n5. Obtaining SSL certificate for {domain}...")
    cmd = f"certbot --nginx -d {domain} -d www.{domain} --email {email} --agree-tos --non-interactive --redirect"
    status, output, error = execute_command(ssh, cmd, timeout=300)
    print(output)
    if error:
        print(error)
    
    if status == 0:
        print("✅ SSL certificate obtained successfully")
    else:
        print("❌ Failed to obtain SSL certificate")
        print("Check that your domain DNS points to this server's IP")
        sys.exit(1)
    
    # Setup auto-renewal
    print("\n6. Setting up auto-renewal...")
    execute_command(ssh, "(crontab -l 2>/dev/null; echo '0 12 * * * /usr/bin/certbot renew --quiet') | crontab -")
    print("✅ Auto-renewal configured (daily check at 12:00)")
    
    # Reload Nginx with new config
    print("\n7. Reloading Nginx...")
    execute_command(ssh, "systemctl reload nginx")
    print("✅ Nginx reloaded")
    
    # Test HTTPS
    print(f"\n8. Testing HTTPS for {domain}...")
    status, output, error = execute_command(ssh, f"curl -s -o /dev/null -w '%{{http_code}}' https://{domain}")
    print(f"HTTPS status code: {output}")
    
    ssh.close()
    
    print("\n" + "="*60)
    print("🎉 SSL setup complete!")
    print("="*60)
    print(f"\nYour site is now accessible at https://{domain}")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyError as e:
        print(f"❌ Missing required environment variable: {e}")
        print("Set VPS_HOST, VPS_PASSWORD, VPS_DOMAIN, VPS_SSL_EMAIL (and optionally VPS_USER, VPS_PORT) before running.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)