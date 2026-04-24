# 🤝 Contribuindo

Bem-vindo. Este é um re
po de demonstração para entrevista técnica

**AI Engineer · Mouts IT × AmBev**, mas pu
ll requests externos são
bem-vindos para cor
reções de bugs e melhorias de documentaçã
o.

## 🧭 Onde começar

| Quero… | Vá p
ara… |
|---|---|
| Entender a arquitetura |
 [`docs/arquimedes.md`](docs/arquimedes.md) |

| Entender o RAG | [`docs/arquimedes-rag.md`
](docs/arquimedes-rag.md) |
| Conectar via MC
P | [`docs/arquimedes-mcp.md`](docs/arquimede
s-mcp.md) |
| Ver traces no LangSmith | [`doc
s/observability.md`](docs/observability.md) |

| Treinar a LoRA do zero | [`arquimedes/fine
tuning/README.md`](arquimedes/finetuning/READ
ME.md) |
| Subir no VPS | [`deploy/README.md`
](deploy/README.md) |
| Roadmap pendente | [`
TODO.md`](TODO.md) |

## 🛠️ Setup local


```bash
git clone https://github.com/Finish-
Him/agents-demo.git
cd agents-demo
python -m 
venv .venv && source .venv/bin/activate
pip i
nstall -r requirements.txt
cp .env.example .e
nv   # preencha as chaves
python -m arquimede
s.rag.ingest --reset
python api.py          #
 http://localhost:8000
```

Frontend separado
:
```bash
cd frontend && npm install && npm r
un dev
```

## ✅ Antes de abrir um PR

1. *
*Testes**: `python -m pytest tests/ -q` deve 
ficar verde (≥ 142 testes).
2. **Build do f
rontend**: `cd frontend && npm run build` dev
e compilar
   sem erros TS.
3. **Tipagem**: e
vite `any` no TypeScript; use Pydantic ou `Ba
seModel`
   no Python para entradas/saídas e
struturadas.
4. **Naming**: `snake_case` em P
ython, `PascalCase` em componentes
   React, 
`kebab-case.spec.ts` em testes Playwright.
5.
 **Commits**: mensagens no formato
   `<scope
>(<area>): <ação>` — ex.: `feat(arquimede
s): adiciona X`,
   `fix(rag): corrige Y`, `d
ocs(observability): atualiza Z`.
6. **PR**: e
xplique o **porquê** no corpo, não só o qu
ê. Se for um
   bug fix, descreva o sintoma 
e a causa-raiz.

## 🧱 Padrões de código


- **Tools novas**: decoradas com `@tool` em 
`arquimedes/tools/<nome>.py`
  e exportadas e
m `arquimedes/tools/__init__.py` (entram auto
maticamente
  em `all_tools`, que alimenta ta
nto LangGraph quanto MCP).
- **Memory backend
s novos**: implementem `put`, `search`, `get`
,
  `delete` retornando `StoreRecord` de `sha
red/store_types.py`. O
  factory `shared/memo
ry.py:get_store()` faz a seleção via env.
-
 **LLM providers novos**: estendem `_PROVIDER
_PREFIXES` em
  `shared/llm.py` e implementam
 o branch dentro de `get_llm()`.
- **Document
ação**: PT-BR é o padrão. Use emojis em h
eadings (👍) mas
  com moderação no corpo
.

## 🔐 Segurança

- **Nunca** commite `.
env`. Confira com `git status` antes de cada

  commit. O `.gitignore` já protege, mas dou
ble-check.
- Chaves de API rotacionam a cada 
entrevista — evite hardcoded.
- Para o MCP 
server SSE em produção, ponha um reverse-pr
oxy com auth
  (a porta 8765 não tem autenti
cação nativa).

## 🐛 Reportando bugs

Ab
ra uma issue com:

1. O que você tentou (`cu
rl`, comando ou screenshot).
2. O que esperav
a.
3. O que aconteceu (logs do `/tmp/api.log`
 ou console do browser).
4. Versão / commit 
hash (`git rev-parse --short HEAD`).


