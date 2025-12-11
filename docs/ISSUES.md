# Backlog de Issues Prioritárias

## 1. Fechar a migração para repositório leve
- **Contexto:** O `MIGRATION_PLAN.md` pede compactar histórico V5/V6 (~40 GB) e manter apenas V7 + `Legacy/V5_src.zip` local.
- **Riscos:** Repositório pesado bloqueia colaboradores e CI/CD.
- **Próximos passos:**
  - Compactar pastas V5/V6 e enviar para Google Drive conforme plano.
  - Criar diretório `Legacy/` com `V5_src.zip` e remover artefatos locais grandes.
  - Atualizar `.gitignore` caso novos arquivos temporários sejam gerados.

## 2. Coletor automatizado DreamLeague S27
- **Contexto:** PRD exige ingestão contínua (24 times, últimas 100 partidas, rosters e estatísticas individuais) via OpenDota/Steam.
- **Riscos:** Dashboards e Multi-AI ficam desatualizados sem dados recentes.
- **Próximos passos:**
  - Implementar script de coleta incremental (ex.: `scripts/dreamleague_collect.py`).
  - Armazenar em Supabase com fallback JSON; documentar esquema e agendamento (cron/GitHub Actions/VPS).
  - Adicionar testes de sanidade para times/partidas e monitoramento de falhas de API.

## 3. Robustez do Multi-AI/OpenRouter
- **Contexto:** `src/multi_ai.py` aceita `OPENROUTER_API_KEY=None` e captura exceções genéricas, retornando strings de erro.
- **Riscos:** Falhas silenciosas e respostas vazias em produção.
- **Próximos passos:**
  - Validar presença do token antes das chamadas e retornar erro estruturado.
  - Diferenciar erros de rede, limite de tokens e tempo excedido.
  - Logar falhas de providers para troubleshooting (Streamlit + logs VPS).

## 4. Validação e fallback de dados (Supabase/JSON)
- **Contexto:** `src/database.py` usa try/except amplo e pode ocultar problemas de conexão ou ausência de dados.
- **Riscos:** Dados inconsistentes sem alertas; dashboards podem exibir informações antigas.
- **Próximos passos:**
  - Restringir exceções capturadas e propagar erros críticos.
  - Adicionar logs/alertas quando cair para JSON ou quando datasets estiverem vazios.
  - Criar checagens de integridade para arquivos locais e tabelas Supabase.

## 5. Deploy e observabilidade
- **Contexto:** Deploy principal no Streamlit Cloud e VPS (AlmaLinux + Nginx). Precisa de rotina consistente de publicação e monitoração.
- **Riscos:** Divergência de versões entre Streamlit/VPS; downtime não detectado.
- **Próximos passos:**
  - Padronizar checklist de deploy (git pull, dependências, restart de serviço) e automatizar via `deploy.sh`/CI.
  - Configurar healthcheck e alertas básicos (status da porta 8501/Streamlit Cloud, logs em `/opt/prometheus/logs`).
  - Documentar rollback rápido em caso de falha.

## 6. QA e testes mínimos
- **Contexto:** Módulos críticos (IA, odds, notificações) não têm suíte de testes descrita.
- **Riscos:** Regressões em produção e inconsistência de modelos/limites.
- **Próximos passos:**
  - Definir testes de fumaça para APIs externas (OpenDota, Steam, OpenRouter) com mocks ou limites baixos.
  - Checar tamanho e disponibilidade dos JSON locais antes de carregar no app.
  - Automatizar execução em CI/CD e antes de cada deploy.
