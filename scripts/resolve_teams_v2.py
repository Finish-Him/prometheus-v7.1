"""
OpenDota Team ID Resolver V2
Busca times usando /proMatches e /teams endpoints
"""
import requests
import json
import time

API_KEY = '00495232-b2b4-4d0b-87e3-c01de846c4b4'
BASE = 'https://api.opendota.com/api'

# Times conhecidos (já temos os IDs)
KNOWN_TEAMS = {
    'Team Spirit': 7119388,
    'Team Liquid': 2163,
    'Tundra Esports': 8291895,
    'OG': 2586976,
    'Nigma Galaxy': 7554697,
    'Virtus.pro': 1883502,
    'Natus Vincere': 36,
    'Xtreme Gaming': 8599101
}

# Times a buscar
TEAMS_TO_FIND = [
    'Team Falcons', 'Falcons',
    'BetBoom', 'BB Team',
    'PARIVISION', 'Pari',
    'HEROIC',
    'Aurora', 'Aurora Gaming',
    'MOUZ', 'Mouz',
    'GamerLegion',
    'Amaru',
    '1win',
    'Gaimin Gladiators',
    'nouns',
    'Talon',
    'Entity'
]

print('=' * 60)
print('PROMETHEUS V7 - Team ID Resolver V2')
print('=' * 60)

# 1. Buscar times recentes via /proMatches
print('\n[1] Buscando partidas profissionais recentes...')
r = requests.get(f'{BASE}/proMatches', params={'api_key': API_KEY})
pro_matches = r.json()[:100]  # Últimas 100 partidas pro

# Extrair times únicos
teams_from_matches = {}
for match in pro_matches:
    for key in ['radiant_name', 'dire_name']:
        name = match.get(key)
        team_id = match.get(key.replace('_name', '_team_id'))
        if name and team_id:
            teams_from_matches[name] = team_id

print(f'   Encontrados {len(teams_from_matches)} times em partidas recentes')

# 2. Buscar times via /teams (top por rating)
print('\n[2] Buscando times top por rating...')
r = requests.get(f'{BASE}/teams', params={'api_key': API_KEY})
all_teams = r.json()[:500]  # Top 500 times

teams_by_name = {t['name']: t['team_id'] for t in all_teams if t.get('name')}
teams_by_tag = {t['tag']: t['team_id'] for t in all_teams if t.get('tag')}

print(f'   Carregados {len(teams_by_name)} times do ranking')

# 3. Combinar resultados
print('\n[3] Combinando resultados...')
all_found = {**KNOWN_TEAMS}

# Adicionar times das partidas pro
for name, team_id in teams_from_matches.items():
    if name not in all_found:
        all_found[name] = team_id

# Buscar times específicos
print('\n[4] Buscando times específicos...')
search_results = {}

for term in TEAMS_TO_FIND:
    # Busca por nome
    for name, tid in teams_by_name.items():
        if term.lower() in name.lower():
            search_results[name] = tid
    # Busca por tag
    for tag, tid in teams_by_tag.items():
        if term.lower() in tag.lower():
            # Pegar o nome do time
            for t in all_teams:
                if t['team_id'] == tid:
                    search_results[t['name']] = tid
                    break

# Combinar tudo
all_found.update(search_results)

print('\n' + '=' * 60)
print('RESULTADOS FINAIS')
print('=' * 60)

# Ordenar por nome
for name in sorted(all_found.keys()):
    print(f'{name}: {all_found[name]}')

print('\n' + '=' * 60)
print(f'Total: {len(all_found)} times')
print('=' * 60)

# Salvar
with open('team_ids_all.json', 'w', encoding='utf-8') as f:
    json.dump(all_found, f, indent=2, ensure_ascii=False)

print('\nSalvo em team_ids_all.json')

# Listar times do DreamLeague que ainda precisamos
print('\n' + '=' * 60)
print('TIMES DO DREAMLEAGUE S27')
print('=' * 60)

dreamleague_teams = [
    'Team Falcons', 'Xtreme Gaming', 'Team Spirit', 'Team Liquid',
    'Tundra Esports', 'BetBoom Team', 'PARIVISION', 'HEROIC',
    'Nigma Galaxy', 'OG', 'Aurora Gaming', 'Natus Vincere',
    'Virtus.pro', 'MOUZ', 'GamerLegion', 'Amaru Gaming',
    'Runa Team', 'Yakult Brothers', 'Team Nemesis', 'Team Yandex',
    '1win Team', 'Pipsqueak+4', 'Passion UA', 'Team Tidebound'
]

found_dl = {}
not_found_dl = []

for team in dreamleague_teams:
    found = False
    for name, tid in all_found.items():
        if team.lower() in name.lower() or name.lower() in team.lower():
            found_dl[team] = tid
            found = True
            break
    if not found:
        not_found_dl.append(team)

print('\nEncontrados:')
for name, tid in found_dl.items():
    print(f'  [OK] {name}: {tid}')

print('\nNao encontrados:')
for name in not_found_dl:
    print(f'  [--] {name}')

# Salvar mapeamento DreamLeague
with open('dreamleague_team_ids.json', 'w', encoding='utf-8') as f:
    json.dump({'found': found_dl, 'not_found': not_found_dl}, f, indent=2, ensure_ascii=False)
