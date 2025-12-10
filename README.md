# 🔥 PROMETHEUS V7.3

> **Plataforma Profissional de Análise e Previsão para Dota 2 - DreamLeague Season 27**

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://prometheusv7.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Finish--Him%2Fprometheus--v7.1-blue)](https://github.com/Finish-Him/prometheus-v7.1)

## 📋 Sobre o Projeto

Prometheus é uma plataforma avançada de análise e previsão para **Dota 2 Profissional**, especializada na **DreamLeague Season 27** e outros torneios tier 1. O sistema combina múltiplas IAs (Gemini, GPT-4o, Claude), análise de dados em tempo real e gestão de apostas.

### ✨ Principais Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🎯 **Match Hub** | Tracking ao vivo via Steam API + Schedule DreamLeague |
| 🤖 **Multi-AI Analysis** | Análise com consensus de Gemini 2.5, GPT-4o, Claude Opus |
| 📊 **Analytics 2025** | 23.000+ partidas com estatísticas detalhadas |
| 🦅 **Draft Analyzer** | Análise de composições e previsões de draft |
| 💰 **Odds Tracker** | Registro de odds + Kelly Criterion |
| 📧 **Notifications** | Email com relatórios PDF 2h antes das partidas |
| ⏰ **Countdown** | Horas/minutos até próxima partida (GMT-3) |

## 📁 Estrutura do Projeto

```
Sistema Prometheus/
├── app.py                     # 🚀 Entrada principal (Streamlit)
├── src/                       # Módulos Python
│   ├── database.py            # Supabase + JSON fallback
│   ├── multi_ai.py            # Multi-AI Engine (Gemini/GPT/Claude)
│   ├── steam_api.py           # Steam Web API client
│   ├── hero_mapper.py         # Hero ID → name/image
│   ├── analytics.py           # Analytics & predictions
│   ├── draft_analyzer.py      # Draft composition analysis
│   ├── odds_tracker.py        # Odds tracking system
│   └── notifications.py       # Email & countdown system
├── Database/
│   ├── Json/leagues/          # DreamLeague S27 data
│   ├── Json/teams/            # Pro teams data
│   ├── Json/heroes/           # Hero metadata
│   └── supabase_schema.sql    # DB schema
├── scripts/                   # Data collection scripts
├── Agentes/Arquimedes/        # MCP Agent orchestrator
├── .streamlit/config.toml     # Streamlit config
├── requirements.txt           # Dependencies
└── .env                       # API keys (não versionado)
```

## 🚀 Quick Start

### Opção 1: Streamlit Cloud (Recomendado)
Acesse: **https://prometheusv7.streamlit.app/**

### Opção 2: Local
```powershell
# Clone o repositório
git clone https://github.com/Finish-Him/prometheus-v7.1.git
cd prometheus-v7.1

# Crie ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edite .env com suas chaves

# Execute
streamlit run app.py
```

### Opção 3: Script Launcher
```powershell
.\run.ps1
```

## 🔑 APIs Configuradas

| API | Uso | Limite |
|-----|-----|--------|
| **Supabase** | Banco de dados | Unlimited |
| **OpenDota** | Dados históricos | 3000 req/min (Premium) |
| **Steam Web API** | Partidas ao vivo | 100K/day |
| **OpenRouter** | Multi-AI (Gemini/GPT/Claude) | Pay per use |

## 📊 Dados Disponíveis

| Métrica | Valor |
|---------|-------|
| **Partidas 2025** | 23,420+ |
| **Picks/Bans** | 551,620 |
| **Objectives** | 493,881 |
| **Teamfights** | 197,246 |
| **Heróis** | 124 |
| **Times DreamLeague** | 24 |

## 🎮 DreamLeague S27 - Schedule

**Datas:** 09-20 Dezembro 2025  
**Local:** Stockholm, Sweden  
**Prize Pool:** $1,000,000  
**Formato:** Swiss System (Group) → Double Elimination (Playoffs)

### Rounds Hoje (10/12)
| Horário (BRT) | Match |
|---------------|-------|
| 04:00 | Team Liquid vs Team Nemesis |
| 04:00 | Team Spirit vs 1win Team |
| 04:00 | OG vs Team Tidebound |
| 07:00 | Team Falcons vs Passion UA |
| 07:00 | Tundra Esports vs Amaru Gaming |

## 📧 Email Reports

Configure em `.env`:
```env
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=app-password
EMAIL_TO=moises.costa12345@gmail.com,gabrielol2035@gmail.com
```

Receba:
- ☀️ **Daily Summary** - Partidas do dia (manhã)
- 📄 **Match Report PDF** - Análise detalhada 2h antes de cada série

## 🔧 Módulos V7.3

### Multi-AI Analysis
```python
from src.multi_ai import sync_analyze_match
result = sync_analyze_match("Team Falcons", "Passion UA")
# Usa Gemini + GPT-4o + Claude para consensus
```

### Draft Analyzer
```python
from src.draft_analyzer import analyze_single_draft
analysis = analyze_single_draft(
    radiant=["Pudge", "Invoker", "Anti-Mage", "Lion", "Tidehunter"],
    dire=["Phantom Assassin", "Storm Spirit", "Axe", "Shadow Shaman", "Witch Doctor"]
)
```

### Odds Tracker
```python
from src.odds_tracker import get_tracker
tracker = get_tracker()
tracker.add_odds("Team Falcons vs Passion UA", 1.45, 2.80, "bet365")
```

## 📅 Versões

| Versão | Data | Status |
|--------|------|--------|
| **V7.3** | 10/12/2025 | ✅ Atual - Multi-AI + Notifications |
| V7.2 | 09/12/2025 | Match Hub + Steam API |
| V7.1 | 08/12/2025 | Supabase Migration |
| V7.0 | 07/12/2025 | Initial Release |

---

**Última atualização**: 10/12/2025  
**Autor**: Prometheus Team  
**Licença**: Privado
