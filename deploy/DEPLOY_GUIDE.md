# Prometheus V7 - VPS Deployment Guide
# Hostinger VPS - AlmaLinux 9 with cPanel

## 📋 Informações do Servidor

| Item | Valor |
|------|-------|
| **IP** | 72.62.9.90 |
| **Hostname** | srv1180544.hstgr.cloud |
| **OS** | AlmaLinux 9 with cPanel |
| **SSH** | `ssh root@72.62.9.90` |
| **Domínio** | prometheus.mscconsultoriarj.com.br |
| **Porta App** | 8501 (interno) |

---

## 🚀 Deploy Inicial (Primeira vez)

### 1. Conectar via SSH

```bash
ssh root@72.62.9.90
# Senha: Moises@24512987
```

### 2. Upload do script de setup

No **PowerShell** do Windows:
```powershell
scp deploy/setup_vps.sh root@72.62.9.90:/root/
```

### 3. Executar setup no servidor

```bash
chmod +x /root/setup_vps.sh
./setup_vps.sh
```

### 4. Configurar .env

```bash
nano /opt/prometheus/app/.env
```

Adicionar:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-xxx
OPENDOTA_API_KEY=xxx
```

### 5. Configurar SSL (HTTPS)

```bash
# Instalar certbot
dnf install -y certbot python3-certbot-nginx

# Gerar certificado
certbot --nginx -d prometheus.mscconsultoriarj.com.br

# Auto-renovação
systemctl enable certbot-renew.timer
```

---

## 🔄 Deploy de Atualizações

### Opção 1: Via SSH Manual

```bash
ssh root@72.62.9.90
cd /opt/prometheus/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart prometheus
```

### Opção 2: Script de deploy

```bash
ssh root@72.62.9.90
./deploy.sh
```

### Opção 3: PowerShell do Windows

```powershell
.\deploy\deploy_windows.ps1
```

---

## 📊 Comandos Úteis

### Status do serviço
```bash
systemctl status prometheus
```

### Ver logs em tempo real
```bash
journalctl -u prometheus -f
```

### Reiniciar aplicação
```bash
systemctl restart prometheus
```

### Ver logs da aplicação
```bash
tail -f /opt/prometheus/logs/prometheus.log
tail -f /opt/prometheus/logs/prometheus-error.log
```

### Verificar Nginx
```bash
nginx -t
systemctl status nginx
```

### Verificar portas
```bash
ss -tlnp | grep -E '(8501|80|443)'
```

---

## 🔧 Troubleshooting

### App não inicia
```bash
# Verificar logs
journalctl -u prometheus -n 50

# Testar manualmente
cd /opt/prometheus/app
source venv/bin/activate
streamlit run app.py --server.port=8501
```

### Erro de dependências
```bash
cd /opt/prometheus/app
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Nginx 502 Bad Gateway
```bash
# Verificar se app está rodando
systemctl status prometheus

# Reiniciar tudo
systemctl restart prometheus
systemctl restart nginx
```

### Permissões
```bash
chown -R prometheus:prometheus /opt/prometheus
chmod -R 755 /opt/prometheus/app
```

---

## 📁 Estrutura no Servidor

```
/opt/prometheus/
├── app/                    # Código da aplicação
│   ├── app.py             # Entry point
│   ├── src/               # Módulos Python
│   ├── Database/          # JSONs e dados
│   ├── requirements.txt   # Dependências
│   └── venv/              # Virtual environment
├── logs/                   # Logs da aplicação
│   ├── prometheus.log
│   └── prometheus-error.log
└── backups/               # Backups
```

---

## 🔐 Segurança

### Firewall
```bash
# Verificar regras
firewall-cmd --list-all

# Adicionar regra
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload
```

### Fail2ban (recomendado)
```bash
dnf install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📈 Monitoramento

### Uso de recursos
```bash
htop
df -h
free -m
```

### Conexões ativas
```bash
ss -s
netstat -an | grep ESTABLISHED | wc -l
```

---

## 🌐 URLs

- **Aplicação**: http://prometheus.mscconsultoriarj.com.br
- **Após SSL**: https://prometheus.mscconsultoriarj.com.br
- **API Hostinger**: Bearer 1r66kOsRcsS56BvbZ0aWhzDxSVxHF2Lh9I4awa6u4ef04e0c
