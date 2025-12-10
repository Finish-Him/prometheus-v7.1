# ⚙️ PROMETHEUS V7 - Guia de Setup

> **Versão**: 7.0.1  
> **Data**: 09/12/2025  
> **Sistema Operacional**: Windows 10/11

---

## 📋 Índice

1. [Requisitos](#1-requisitos)
2. [APIs e Credenciais](#2-apis-e-credenciais)
3. [Estrutura de Pastas](#3-estrutura-de-pastas)
4. [Instalação](#4-instalação)
5. [Configuração](#5-configuração)
6. [Primeiro Uso](#6-primeiro-uso)

---

## 1. Requisitos

### Software Necessário

| Software | Versão | Download |
|----------|--------|----------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Git | 2.40+ | [git-scm.com](https://git-scm.com) |
| VS Code | Latest | [code.visualstudio.com](https://code.visualstudio.com) |
| pnpm | 8+ | `npm install -g pnpm` |

### Extensões VS Code Recomendadas

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-toolsai.jupyter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

---

## 2. APIs e Credenciais

### APIs Necessárias

| API | Uso | Onde Obter |
|-----|-----|------------|
| **Steam Web API** | Dados ao vivo de partidas | [steamcommunity.com/dev](https://steamcommunity.com/dev) |
| **OpenDota API** | Dados históricos de partidas | [opendota.com/api-keys](https://www.opendota.com/api-keys) |
| **OpenRouter** | LLMs (Claude, GPT) | [openrouter.ai](https://openrouter.ai) |

### Arquivo de Credenciais (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
# Steam API
STEAM_API_KEY=sua_chave_steam_aqui (Your Steam Web API Key
Key: 116EF013E6A8537842C3436DE9FD7007)

# OpenDota API
OPENDOTA_API_KEY=00495232-b2b4-4d0b-87e3-c01de846c4b4

# OpenRouter (para LLMs)
OPENROUTER_API_KEY=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

# Configurações Gerais
DEBUG=false
LOG_LEVEL=INFO
```

### Onde as credenciais são usadas

| Variável | Módulo | Função |
|----------|--------|--------|
| `STEAM_API_KEY` | `services/steam_api.py` | Dados ao vivo |
| `OPENDOTA_API_KEY` | `services/opendota.py` | Histórico de partidas |
| `OPENROUTER_API_KEY` | `services/llm_service.py` | Análises com IA |

---

## 3. Estrutura de Pastas

### Estrutura Mínima Necessária

```
Sistema Prometheus/
├── v7.0.1/                          # Versão atual
│   ├── Agentes/
│   │   └── Arquimedes/V1.0/         # Orquestrador IA
│   ├── Configurações/
│   │   ├── Apis do Projeto          # Chaves de API
│   │   ├── Skils/
│   │   ├── Sub agentes/
│   │   └── Treinamentos/
│   ├── Database/
│   │   ├── Json/                    # Base de dados
│   │   └── docs/                    # Documentação
│   ├── Images/
│   │   └── Heroes/                  # 124 imagens
│   └── Jupiter notebook/
│       └── *.ipynb
├── .env                             # Credenciais
├── DOCUMENTATION.md                 # Este arquivo
├── INVENTORY.md                     # Inventário
└── README.md                        # Intro
```

---

## 4. Instalação

### 4.1 Clone ou Copie o Projeto

```powershell
# Se for novo clone
git clone <repository-url> "Sistema Prometheus"
cd "Sistema Prometheus"

# Se for cópia local, apenas navegue
cd "C:\Users\Festeja\Desktop\Sistema Prometheus"
```

### 4.2 Instale Dependências Python (para scripts V5)

```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 4.3 Dependências Python (requirements.txt)

```txt
# Core
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# Backend API
fastapi>=0.100.0
uvicorn>=0.22.0
requests>=2.31.0

# Database
sqlalchemy>=2.0.0
alembic>=1.11.0

# Data Science & Analysis
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
jupyter>=1.0.0
notebook>=7.0.0

# Frontend
streamlit>=1.30.0
watchdog>=3.0.0

# Utilities
tqdm>=4.65.0
loguru>=0.7.0
paramiko
```

### 4.4 Instale Dependências do Arquimedes (Node.js)

```powershell
cd "v7.0.1\Agentes\Arquimedes\V1.0"

# Instalar com pnpm
pnpm install

# Ou com npm
npm install
```

---

## 5. Configuração

### 5.1 Configurar Variáveis de Ambiente

1. Copie o template de credenciais:
```powershell
copy CREDENTIALS_TEMPLATE.env .env
```

2. Edite o `.env` com suas chaves de API

### 5.2 Configurar Arquimedes

1. Navegue até a pasta do Arquimedes:
```powershell
cd "v7.0.1\Agentes\Arquimedes\V1.0"
```

2. Configure o `config.json`:
```json
{
  "version": "1.0.0",
  "agents": {
    "manus": { "enabled": true },
    "gen": { "enabled": true },
    "gpt": { "enabled": true }
  },
  "integrations": {
    "github": { "enabled": true },
    "google_cloud": { "enabled": false },
    "openrouter": { "enabled": true }
  }
}
```

### 5.3 Verificar Base de Dados

Certifique-se de que os arquivos JSON principais existem:

```
Database/Json/
├── DATABASE_INDEX.json     ✓ Obrigatório
├── agents/gem/             ✓ Sistema GEM
├── epl_2025_2026/          ✓ Dados da temporada
├── heroes/heroes_meta.json ✓ Meta de heróis
└── config/                 ✓ Constantes
```

---

## 6. Primeiro Uso

### 6.1 Iniciar o Arquimedes (Development)

```powershell
cd "v7.0.1\Agentes\Arquimedes\V1.0"
pnpm dev
```

Acesse: `http://localhost:3000`

### 6.2 Usar Jupyter Notebooks

1. Abra VS Code na pasta do projeto
2. Abra um arquivo `.ipynb` em `Jupiter notebook/`
3. Selecione o kernel Python do ambiente virtual
4. Execute as células

### 6.3 Executar Scripts Python (Legado V5)

```powershell
# Ativar ambiente
.\.venv\Scripts\Activate.ps1

# Executar dashboard Streamlit
streamlit run src/ui/app.py
```

### 6.4 Consultar Documentação

| Preciso de... | Arquivo |
|---------------|---------|
| Entender o projeto | `DOCUMENTATION.md` |
| Ver inventário | `INVENTORY.md` |
| Base de conhecimento | `Database/docs/knowledge_base/` |
| Sistema GEM | `Database/docs/knowledge_base/GEM_SYSTEM_INSTRUCTIONS.md` |
| Estratégias de apostas | `Database/docs/knowledge_base/05_BETTING_STRATEGIES.md` |

---

## 🔧 Troubleshooting

### Erro: "Python não encontrado"

```powershell
# Verificar instalação
python --version

# Se não encontrar, adicionar ao PATH
# Ou usar caminho completo
C:\Python311\python.exe --version
```

### Erro: "Módulo não encontrado"

```powershell
# Ativar ambiente virtual primeiro
.\.venv\Scripts\Activate.ps1

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "API Key inválida"

1. Verifique se o arquivo `.env` existe
2. Confirme que as chaves estão corretas
3. Verifique se as chaves não expiraram

### Erro: "Arquivo JSON não encontrado"

```powershell
# Verificar se a estrutura existe
Get-ChildItem "v7.0.1\Database\Json" -Directory
```

---

## 📞 Suporte

- **Documentação**: `DOCUMENTATION.md`
- **Knowledge Base**: `Database/docs/knowledge_base/`
- **Changelog**: `Database/docs/CHANGELOG.md`

---

*Setup Guide gerado em 09/12/2025 - Prometheus V7.0.1*
