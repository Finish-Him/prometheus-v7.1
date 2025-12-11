# 🎉 Prometheus V7 - Deploy Bem-Sucedido

**Data**: 11 de Dezembro de 2025  
**Servidor**: Hostinger VPS - AlmaLinux 9  
**Status**: ✅ Produção

---

## 📊 Resumo do Deploy

O sistema Prometheus V7.1 foi implantado com sucesso na VPS da Hostinger e está operacional em produção.

| Item | Status | URL/Detalhes |
|------|--------|--------------|
| **Aplicação Web** | ✅ Online | https://prometheus.mscconsultoriarj.com.br |
| **SSL/HTTPS** | ✅ Ativo | Certificado Let's Encrypt válido |
| **Serviço Systemd** | ✅ Rodando | `prometheus.service` |
| **Proxy Reverso** | ✅ Nginx | Configurado na porta 80/443 |
| **Auto-Renewal SSL** | ✅ Configurado | Renovação automática a cada 60 dias |
| **Firewall** | ✅ Configurado | Portas 80 e 443 abertas |

---

## 🏗️ Arquitetura Implantada

```
Internet
    ↓
[Firewall: 80, 443]
    ↓
[Nginx Proxy Reverso]
    ↓
[Streamlit App: 127.0.0.1:8501]
    ↓
[Supabase Database]
```

### Componentes

- **Sistema Operacional**: AlmaLinux 9 with cPanel
- **Web Server**: Nginx 1.20+
- **Application Server**: Streamlit (Python 3.11)
- **Process Manager**: Systemd
- **SSL**: Let's Encrypt (Certbot)
- **Database**: Supabase PostgreSQL (cloud)

---

## 📁 Estrutura no Servidor

```
/opt/prometheus/
├── app/                    # Código da aplicação (git clone)
│   ├── app.py             # Entry point Streamlit
│   ├── src/               # Módulos Python
│   ├── Database/          # Dados JSON (fallback)
│   ├── requirements.txt   # Dependências
│   ├── .env              # Variáveis de ambiente (não versionado)
│   └── venv/             # Ambiente virtual Python
├── logs/                  # Logs da aplicação
│   ├── prometheus.log
│   └── prometheus-error.log
└── backups/               # Backups (futuro)
```

---

## 🔧 Configurações Aplicadas

### 1. Serviço Systemd

**Arquivo**: `/etc/systemd/system/prometheus.service`

```ini
[Unit]
Description=Prometheus V7 - Dota 2 Analytics Platform
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/opt/prometheus/app
Environment="PATH=/opt/prometheus/app/venv/bin:/usr/local/bin:/usr/bin"
Environment="STREAMLIT_SERVER_PORT=8501"
Environment="STREAMLIT_SERVER_ADDRESS=127.0.0.1"

ExecStart=/opt/prometheus/app/venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=127.0.0.1 \
    --server.headless=true

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Comandos úteis**:
```bash
systemctl status prometheus    # Ver status
systemctl restart prometheus   # Reiniciar
journalctl -u prometheus -f    # Ver logs em tempo real
```

### 2. Nginx Proxy Reverso

**Arquivo**: `/etc/nginx/conf.d/prometheus.conf`

```nginx
upstream prometheus_backend {
    server 127.0.0.1:8501;
    keepalive 32;
}

server {
    listen 80;
    server_name prometheus.mscconsultoriarj.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name prometheus.mscconsultoriarj.com.br;

    ssl_certificate /etc/letsencrypt/live/prometheus.mscconsultoriarj.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/prometheus.mscconsultoriarj.com.br/privkey.pem;

    location / {
        proxy_pass http://prometheus_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### 3. Variáveis de Ambiente

**Arquivo**: `/opt/prometheus/app/.env` (criado manualmente, não versionado)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
STEAM_API_KEY=116EF013E6A8537842C3436DE9FD7007
OPENDOTA_API_KEY=00495232-b2b4-4d0b-87e3-c01de846c4b4
OPENROUTER_API_KEY=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
APP_ENV=production
DEBUG=false
```

---

## 🚀 Processo de Deploy Executado

### Fase 1: Preparação do Ambiente
1. ✅ Conexão SSH estabelecida com a VPS
2. ✅ Verificação do sistema operacional (AlmaLinux 9)
3. ✅ Atualização de pacotes do sistema

### Fase 2: Instalação de Dependências
1. ✅ Python 3.11 instalado
2. ✅ Nginx instalado e configurado
3. ✅ Git instalado
4. ✅ Ferramentas de desenvolvimento instaladas

### Fase 3: Configuração da Aplicação
1. ✅ Usuário `prometheus` criado
2. ✅ Repositório clonado do GitHub
3. ✅ Ambiente virtual Python criado
4. ✅ Dependências Python instaladas
5. ✅ Variáveis de ambiente configuradas

### Fase 4: Configuração de Serviços
1. ✅ Serviço systemd criado e habilitado
2. ✅ Nginx configurado como proxy reverso
3. ✅ Firewall configurado (portas 80 e 443)
4. ✅ Conflito com Apache resolvido (Apache desabilitado)

### Fase 5: Segurança (SSL)
1. ✅ Certbot instalado
2. ✅ Certificado SSL obtido do Let's Encrypt
3. ✅ HTTPS configurado automaticamente
4. ✅ Renovação automática configurada

---

## 🔍 Problemas Encontrados e Soluções

### Problema 1: Nginx não iniciava
**Erro**: `bind() to 0.0.0.0:80 failed (98: Address already in use)`

**Causa**: Apache (httpd) do cPanel estava usando a porta 80

**Solução**:
```bash
systemctl stop httpd
systemctl disable httpd
systemctl start nginx
```

### Problema 2: Credenciais de API
**Situação**: Arquivo `.env` não existia no servidor

**Solução**: Criado arquivo `.env.production` localmente e enviado via SFTP para `/opt/prometheus/app/.env`

---

## 📝 Scripts de Deploy Criados

Foram criados scripts automatizados para facilitar futuros deploys e manutenções:

| Script | Propósito | Uso |
|--------|-----------|-----|
| `deploy/setup_vps.sh` | Setup completo do servidor | `./setup_vps.sh` |
| `deploy/deploy_automated.py` | Deploy automatizado via SSH | `python3 deploy_automated.py` |
| `deploy/fix_nginx.py` | Corrigir problemas do Nginx | `python3 fix_nginx.py` |
| `deploy/setup_ssl.py` | Configurar SSL/HTTPS | `python3 setup_ssl.py` |
| `deploy/deploy_to_vps.sh` | Deploy rápido (bash) | `./deploy_to_vps.sh` |

---

## 🔄 Procedimento para Atualizar a Aplicação

Para fazer deploy de novas versões:

```bash
# 1. Conectar ao servidor
ssh root@72.62.9.90

# 2. Ir para o diretório da aplicação
cd /opt/prometheus/app

# 3. Fazer backup (opcional)
cp -r /opt/prometheus/app /opt/prometheus/backups/app-$(date +%Y%m%d-%H%M%S)

# 4. Atualizar código do GitHub
sudo -u prometheus git pull origin main

# 5. Atualizar dependências (se necessário)
sudo -u prometheus ./venv/bin/pip install -r requirements.txt

# 6. Reiniciar serviço
systemctl restart prometheus

# 7. Verificar status
systemctl status prometheus
journalctl -u prometheus -n 50
```

**Ou usar o script automatizado**:
```bash
# No seu computador local
cd prometheus-v7.1
python3 deploy/deploy_automated.py
```

---

## 📊 Monitoramento e Logs

### Ver logs em tempo real
```bash
ssh root@72.62.9.90 'journalctl -u prometheus -f'
```

### Ver últimas 100 linhas de log
```bash
ssh root@72.62.9.90 'journalctl -u prometheus -n 100'
```

### Ver logs de erro
```bash
ssh root@72.62.9.90 'tail -f /opt/prometheus/logs/prometheus-error.log'
```

### Verificar status dos serviços
```bash
ssh root@72.62.9.90 'systemctl status prometheus nginx'
```

### Health check
```bash
curl https://prometheus.mscconsultoriarj.com.br/health
```

---

## 🔐 Segurança

### Certificado SSL
- **Emissor**: Let's Encrypt
- **Validade**: 90 dias
- **Renovação**: Automática (via cron)
- **Algoritmo**: RSA 2048-bit

### Firewall
```bash
firewall-cmd --list-all
# Portas abertas: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

### Permissões
- Aplicação roda como usuário `prometheus` (não-root)
- Diretório `/opt/prometheus` pertence ao usuário `prometheus`
- Arquivo `.env` tem permissões `600` (apenas owner pode ler)

---

## 📞 Informações de Acesso

| Recurso | Detalhes |
|---------|----------|
| **URL Produção** | https://prometheus.mscconsultoriarj.com.br |
| **Servidor SSH** | `ssh root@72.62.9.90` |
| **Hostname** | srv1180544.hstgr.cloud |
| **IP** | 72.62.9.90 |
| **Localização** | São Paulo, Brasil |
| **Repositório** | https://github.com/Finish-Him/prometheus-v7.1 |
| **Streamlit Cloud** | https://prometheusv7.streamlit.app/ |

---

## ✅ Checklist de Verificação

- [x] Aplicação acessível via HTTPS
- [x] SSL válido e funcionando
- [x] Serviço systemd ativo e habilitado
- [x] Nginx proxy reverso configurado
- [x] Logs sendo gerados corretamente
- [x] Variáveis de ambiente configuradas
- [x] Firewall configurado
- [x] Auto-renewal SSL ativo
- [x] Backup do código no GitHub
- [x] Documentação atualizada

---

## 🎯 Próximos Passos (Opcional)

1. **Monitoramento**: Configurar alertas (Uptime Robot, Pingdom)
2. **Backup Automático**: Script para backup diário do banco de dados
3. **CI/CD**: GitHub Actions para deploy automático
4. **Logs Centralizados**: Integração com serviço de logs (Papertrail, Loggly)
5. **Performance**: Configurar cache do Nginx
6. **Escalabilidade**: Considerar load balancer se necessário

---

## 📚 Referências

- [Documentação Streamlit](https://docs.streamlit.io/)
- [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Systemd Service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Deploy realizado por**: Manus AI  
**Data**: 11/12/2025  
**Versão**: Prometheus V7.1  
**Status**: ✅ Produção Estável
