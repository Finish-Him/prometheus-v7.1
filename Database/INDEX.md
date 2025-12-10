# 📁 NEW_DATABASE - Índice de Arquivos

> **Última Atualização**: 08/12/2025
> **Total de Arquivos**: 300+ JSONs, 100+ MDs

---

## 🗂️ Estrutura Completa

```
Database/
├── json/                          # TODOS OS DADOS JSON
│   ├── DATABASE_INDEX.json        # Índice mestre
│   │
│   ├── agents/                    # 🤖 AGENTES IA
│   │   └── gem/                   # Sistema GEM
│   │       ├── GEM_EPL_master.json
│   │       ├── EPL_teams_database.json
│   │       ├── EPL_heroes_meta.json
│   │       ├── EPL_strategy_weights.json
│   │       ├── draft_analyzer.json
│   │       ├── conversation_memory.json
│   │       ├── prediction_validation_log.json
│   │       ├── GPT_Prometheus_config.md
│   │       ├── GEM_Gemini_config.md
│   │       ├── system_evolution_prompt.md
│   │       └── upload_pack/       # Arquivos para upload
│   │
│   ├── heroes/                    # 🦸 HERÓIS
│   │   └── heroes_meta.json       # Meta EPL 40 seasons
│   │
│   ├── teams/                     # 👥 TIMES
│   │   ├── teams.json
│   │   └── team_lynx/             # Dados Team Lynx
│   │       ├── complete.json
│   │       ├── metadata.json
│   │       ├── players.json
│   │       ├── picks_bans.json
│   │       ├── heroes_played.json
│   │       ├── matches.json
│   │       ├── series.json
│   │       ├── drafts.json
│   │       └── counter_picks.json
│   │
│   ├── players/                   # 🎮 JOGADORES
│   │   └── players.json
│   │
│   ├── matches/                   # ⚔️ PARTIDAS
│   │   ├── matchups.json          # H2H
│   │   ├── EPL_HISTORY_COMPLETE.json
│   │   ├── EPL_PLAYER_HERO_STATS.json
│   │   └── HYPER_LEAGUE_STATS.json
│   │
│   ├── leagues/                   # 🏆 LIGAS
│   │   ├── leagues_index.json
│   │   ├── epl_s33.json
│   │   └── league_*.json          # 20+ ligas
│   │
│   ├── epl_2025_2026/            # 📅 EPL TEMPORADA ATUAL
│   │   ├── epl_complete.json
│   │   ├── matches.json
│   │   ├── teams.json
│   │   ├── teams_detailed.json
│   │   ├── teams_overview.json
│   │   ├── players-epl.json
│   │   ├── players_rankings.json
│   │   ├── heroes.json
│   │   ├── heroes_stats.json
│   │   ├── heroes_picks_bans.json
│   │   ├── heroes_contested.json
│   │   ├── picks_bans.json
│   │   ├── drafts.json
│   │   ├── series.json
│   │   ├── scores.json
│   │   └── metadata.json
│   │
│   ├── opendota/                  # 📊 OPENDOTA RAW DATA
│   │   └── 2025/
│   │       ├── 2025_master.json
│   │       ├── 202501/ → 202512/  # Por mês
│   │       │   ├── *_master.json
│   │       │   ├── main_metadata.json
│   │       │   ├── picks_bans.json
│   │   │   │   ├── teams.json
│   │       │   ├── teamfights.json
│   │       │   ├── objectives.json
│   │       │   ├── draft_timings.json
│   │       │   ├── radiant_gold_adv.json
│   │       │   ├── radiant_exp_adv.json
│   │       │   ├── chat.json
│   │       │   ├── cosmetics.json
│   │       │   └── all_word_counts.json
│   │
│   ├── odds/                      # 💰 ODDS
│   │   └── rivalry/
│   │       ├── all_odds_consolidated.json
│   │       └── *_vs_*.json        # Odds por partida
│   │
│   ├── bets/                      # 🎰 APOSTAS
│   │   ├── user_bets.json
│   │   └── settled_bets.json
│   │
│   ├── events/                    # 📆 EVENTOS
│   │   └── upcoming.json
│   │
│   ├── predictions/               # 🔮 PREVISÕES
│   │   └── *.json                 # Previsões salvas
│   │
│   └── config/                    # ⚙️ CONFIGURAÇÕES
│       ├── config.json
│       ├── database.json
│       ├── heroes.json
│       ├── items.json
│       ├── itemids.json
│       ├── abilities.json
│       ├── abilitiesid.json
│       ├── heroabilitiesandtalents.json
│       ├── aghanimheroupgrades.json
│       ├── herolore.json
│       ├── leagues.json
│       ├── regions.json
│       ├── gamemodes.json
│       ├── chatwheel.json
│       ├── patch.json
│       └── patchnotes.json
│
└── docs/                          # 📚 DOCUMENTAÇÃO
    ├── README.md
    ├── CHANGELOG.md
    │
    ├── projeto/                   # 🎯 PROJETO
    │   ├── PROJETO_COMPLETO.md    # ← VOCÊ ESTÁ AQUI
    │   ├── PROMETHEUS_INDEX.md
    │   ├── STRUCTURE.md
    │   ├── PROJECT_STRUCTURE.md
    │   └── ERROR_LOG.md
    │
    ├── releases/                  # 📦 RELEASES
    │   ├── V5.5.0_RELEASE_NOTES.md
    │   ├── V5.4.2_RELEASE_NOTES.md
    │   ├── V5.4.1_NOTES.md
    │   ├── V5.3.x releases
    │   └── V5.2_RELEASE_NOTES.md
    │
    ├── knowledge_base/            # 🧠 BASE DE CONHECIMENTO
    │   ├── 00-10 arquivos base
    │   ├── GEM_SYSTEM_INSTRUCTIONS.md
    │   ├── PATCH_7.39.md
    │   └── november_2025/         # Análise Nov 2025
    │       └── 00-14 relatórios
    │
    ├── analysis/                  # 📈 ANÁLISES
    │   ├── HYPER_ANALYSIS_REPORT.md
    │   ├── EPL_PLAYER_HERO_REPORT.md
    │   └── EPL_HISTORY_REPORT.md
    │
    ├── leagues/                   # 🏆 LIGAS
    │   ├── LEAGUES_INDEX.md
    │   ├── EPL_SEASON_33.md
    │   └── LIGAS_RAW.md
    │
    ├── api/                       # 🔌 API
    │   ├── OPENDOTA.md
    │   └── DATABASE_SCHEMA.md
    │
    ├── guides/                    # 📖 GUIAS
    │   ├── HOSTINGER.md
    │   ├── MIGRATION_STATUS.md
    │   └── LIGAS.md
    │
    ├── tarefas/                   # ✅ TAREFAS
    │   ├── ROADMAP.md
    │   ├── README.md
    │   ├── DEPLOY_STATUS.md
    │   └── MSC-SYSTEM.md
    │
    ├── agentes/                   # 🤖 AGENTES
    │   └── Arquimede-agente.md
    │
    ├── deploy/                    # 🚀 DEPLOY
    │   └── DEPLOY_PLAN_v5.6.0.md
    │
    ├── lessons/                   # 📝 LIÇÕES
    │   └── SPRINT_V54_RETROSPECTIVE.md
    │
    ├── tracker/                   # 🎯 TRACKER
    │   ├── TESTE_MANUAL.md
    │   └── TEST_SCENARIOS.md
    │
    ├── database/                  # 🗄️ DATABASE
    │   └── DATABASE_SCHEMA.md
    │
    └── raw_data/                  # 📄 DADOS BRUTOS
        ├── Análise Dota 2_ Heróis e Meta.md
        ├── Dota 2_ CCT e Europa Pro.md
        ├── Europa Pro League 33 Dota 2.md
        ├── Guia Apostas Dota 2 EPL S33.md
        ├── GEmini-busca profundaEPL.md
        ├── Análise de Desempenho na EPL.md
        ├── Dota 2 2025_ Apostas e Cenário.md
        └── Winter-Bear Dotabuff.md
```

---

## 📊 Estatísticas

| Categoria | Quantidade |
|-----------|------------|
| **JSON Total** | ~300 arquivos |
| **MD Total** | ~100 arquivos |
| **Dados OpenDota** | 12 meses × 12 arquivos |
| **Ligas** | 20+ ligas |
| **Times Detalhados** | 13 times |
| **Heróis Analisados** | 126 |
| **Partidas EPL** | 7.247+ |

---

## 🔍 Busca Rápida

### Por Funcionalidade

| Preciso de... | Vá para... |
|---------------|------------|
| Configurar GEM | `/json/agents/gem/` |
| Ver meta de heróis | `/json/heroes/heroes_meta.json` |
| Dados de times | `/json/teams/` |
| Histórico de partidas | `/json/matches/` |
| Odds de apostas | `/json/odds/` |
| Dados EPL 2025 | `/json/epl_2025_2026/` |
| Dados brutos OpenDota | `/json/opendota/2025/` |
| Constantes do jogo | `/json/config/` |

### Por Tipo de Documento

| Preciso de... | Vá para... |
|---------------|------------|
| Entender o projeto | `/docs/projeto/PROJETO_COMPLETO.md` |
| Notas de versão | `/docs/releases/` |
| Base de conhecimento EPL | `/docs/knowledge_base/` |
| Relatórios de análise | `/docs/analysis/` |
| Como fazer deploy | `/docs/deploy/` |
| Informações de API | `/docs/api/` |

---

*Índice gerado em 08/12/2025 - Prometheus V5.5.0*
