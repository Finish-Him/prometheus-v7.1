# 🚀 PROMETHEUS - Plano de Migração para Repositório Leve

> **Data**: 09/12/2025  
> **Objetivo**: Reduzir de ~40GB para ~100MB mantendo funcionalidade

---

## 📊 Situação Atual

| Componente | Tamanho | Status |
|------------|---------|--------|
| **Total do Projeto** | ~39.86 GB | ❌ Muito pesado |
| Versão atual (V7) | ~80 MB | ✅ OK |
| Versões anteriores | ~39.78 GB | ❌ Para Drive |

### Detalhamento dos ~40GB

| Pasta | Tamanho | Destino |
|-------|---------|---------|
| V5 archive | 18.1 GB | ☁️ Drive |
| V5 Json Todas as partidas | 10.02 GB | ☁️ Drive |
| V5 database | 9.96 GB | ☁️ Drive |
| V5 Base-de-Dados | 0.79 GB | ☁️ Drive |
| V6 Completo | 53 MB | ☁️ Drive |
| V5 src (código) | 0.73 MB | 📁 ZIP local |
| **V7 Completo** | **~80 MB** | ✅ **MANTER** |

---

## 🎯 Meta Final

### Estrutura Local (~100 MB)

```
Sistema Prometheus/                  (~100 MB)
├── v7.0.1/                         # Versão ativa
│   ├── Agentes/Arquimedes/         # Orquestrador IA
│   ├── Configurações/              # APIs, Skills
│   ├── Database/                   # Dados + Docs
│   ├── Images/                     # Heróis
│   └── Jupiter notebook/           # Notebooks ML
│
├── Legacy/                         # Referência compactada
│   └── V5_src.zip                  # Código Python (~1 MB)
│
├── DOCUMENTATION.md                # Documentação master
├── INVENTORY.md                    # Inventário completo
├── SETUP_GUIDE.md                  # Guia de instalação
├── MIGRATION_PLAN.md               # Este arquivo
└── README.md                       # Introdução
```

### Estrutura no Drive (~40 GB)

```
Prometheus-Backup-Drive/
├── 📁 Data-Historical/             (~30 GB)
│   ├── V5_database_opendota.zip    # 9.96 GB
│   ├── V5_Json_Todas_Partidas.zip  # 10.02 GB
│   └── V5_archive.zip              # 18.1 GB
│
├── 📁 Versions-Complete/           (~1 GB)
│   ├── V5_Complete.zip             # Backup V5
│   └── V6_Complete.zip             # Backup V6
│
└── 📁 Raw-Data/                    (~0.8 GB)
    └── Base-de-Dados.zip           # Dados brutos
```

---

## 📋 Checklist de Execução

### Fase 1: Preparação (30 min)

- [ ] **1.1** Verificar espaço em disco para compactação temporária
- [ ] **1.2** Criar pasta no Google Drive: `Prometheus-Backup-Drive`
- [ ] **1.3** Fazer backup local dos arquivos `.env` e credenciais

### Fase 2: Compactar Dados Históricos (2-3 horas)

#### 2.1 Compactar V5 database (~10 GB → ~3 GB compactado)
```powershell
cd "c:\Users\Festeja\Desktop\Sistema Prometheus\Versões anteriores\Prometheu V5"
Compress-Archive -Path "database" -DestinationPath "V5_database.zip" -CompressionLevel Optimal
```

#### 2.2 Compactar V5 archive (~18 GB → ~5 GB compactado)
```powershell
Compress-Archive -Path "archive" -DestinationPath "V5_archive.zip" -CompressionLevel Optimal
```

#### 2.3 Compactar V5 Json Todas as partidas (~10 GB → ~3 GB compactado)
```powershell
Compress-Archive -Path "Json Todas as partidas" -DestinationPath "V5_Json_Todas_Partidas.zip" -CompressionLevel Optimal
```

#### 2.4 Compactar V5 Base-de-Dados (~0.8 GB)
```powershell
Compress-Archive -Path "Base-de-Dados" -DestinationPath "V5_Base-de-Dados.zip" -CompressionLevel Optimal
```

### Fase 3: Upload para Google Drive (1-2 horas)

- [ ] **3.1** Upload `V5_database.zip` para Drive
- [ ] **3.2** Upload `V5_archive.zip` para Drive
- [ ] **3.3** Upload `V5_Json_Todas_Partidas.zip` para Drive
- [ ] **3.4** Upload `V5_Base-de-Dados.zip` para Drive
- [ ] **3.5** Verificar integridade dos uploads (comparar tamanhos)

### Fase 4: Backup de Versões Completas (1 hora)

#### 4.1 Compactar V5 completo
```powershell
cd "c:\Users\Festeja\Desktop\Sistema Prometheus\Versões anteriores"
Compress-Archive -Path "Prometheu V5" -DestinationPath "V5_Complete_Backup.zip" -CompressionLevel Optimal
```

#### 4.2 Compactar V6 completo
```powershell
Compress-Archive -Path "Prometheus V6" -DestinationPath "V6_Complete_Backup.zip" -CompressionLevel Optimal
```

- [ ] **4.3** Upload backups completos para Drive
- [ ] **4.4** Verificar integridade

### Fase 5: Criar Versão Leve Local (30 min)

#### 5.1 Criar pasta Legacy com código fonte
```powershell
cd "c:\Users\Festeja\Desktop\Sistema Prometheus"
New-Item -ItemType Directory -Path "Legacy" -Force
Compress-Archive -Path "Versões anteriores\Prometheu V5\src" -DestinationPath "Legacy\V5_src.zip"
```

#### 5.2 Mover V7 para raiz (opcional - reorganização)
```powershell
# Opção 1: Manter estrutura atual
# V7 fica em: Versão atual\Versão 7.0\V7.0\v7.0.1\

# Opção 2: Simplificar para raiz
# Copy-Item -Path "Versão atual\Versão 7.0\V7.0\v7.0.1\*" -Destination "." -Recurse
```

### Fase 6: Limpeza (CUIDADO!)

⚠️ **APENAS APÓS CONFIRMAR UPLOADS NO DRIVE**

#### 6.1 Remover pastas grandes (após backup confirmado)
```powershell
# VERIFICAR ANTES DE EXECUTAR!
# Remover apenas se uploads estiverem OK

# Remove-Item -Path "Versões anteriores" -Recurse -Force
```

#### 6.2 Verificar tamanho final
```powershell
$size = (Get-ChildItem -Path "c:\Users\Festeja\Desktop\Sistema Prometheus" -Recurse | Measure-Object -Property Length -Sum).Sum
Write-Host "Tamanho Final: $([math]::Round($size/1MB,2)) MB"
```

---

## 🔒 Verificações de Segurança

### Antes de Deletar

- [ ] **V1** Todos os ZIPs foram criados com sucesso
- [ ] **V2** Todos os ZIPs foram uploaded para o Drive
- [ ] **V3** Tamanhos no Drive correspondem aos locais
- [ ] **V4** Consegue extrair um arquivo de teste de cada ZIP
- [ ] **V5** Backup de credenciais/APIs está salvo separadamente

### Teste de Integridade

```powershell
# Testar extração de um ZIP
Expand-Archive -Path "V5_database.zip" -DestinationPath "test_extract" -Force
# Verificar conteúdo
Get-ChildItem "test_extract" | Select-Object Name, Length
# Limpar teste
Remove-Item "test_extract" -Recurse -Force
```

---

## 📅 Cronograma Sugerido

| Fase | Duração | Status |
|------|---------|--------|
| Preparação | 30 min | ⏳ |
| Compactação | 2-3 horas | ⏳ |
| Upload Drive | 1-2 horas | ⏳ |
| Backup Versões | 1 hora | ⏳ |
| Criar Leve | 30 min | ⏳ |
| Limpeza | 15 min | ⏳ |
| **Total** | **~6 horas** | |

---

## 📝 Notas Importantes

### O que NÃO deletar

1. **Pasta V7.0.1 inteira** - É a versão de trabalho
2. **Arquivos de documentação** na raiz
3. **Credenciais e .env** - Backup separado
4. **ZIP do código V5** em Legacy/

### O que pode ser deletado com segurança (após backup)

1. `Versões anteriores/Prometheu V5/database/`
2. `Versões anteriores/Prometheu V5/archive/`
3. `Versões anteriores/Prometheu V5/Json Todas as partidas/`
4. `Versões anteriores/Prometheu V5/Base-de-Dados/`
5. Pasta `Prometheus V6/` completa

### Recuperação

Se precisar dos dados novamente:
1. Baixe o ZIP do Google Drive
2. Extraia na mesma estrutura original
3. Os paths devem funcionar normalmente

---

## ✅ Resultado Esperado

| Antes | Depois |
|-------|--------|
| ~40 GB local | ~100 MB local |
| Estrutura complexa | Estrutura simplificada |
| Difícil de transportar | Fácil de clonar/copiar |
| Dados históricos misturados | Dados organizados no Drive |

---

*Plano de Migração criado em 09/12/2025*
