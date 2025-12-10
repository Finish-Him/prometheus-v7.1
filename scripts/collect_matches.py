"""
OpenDota Match Collector - DreamLeague S27
Coleta as últimas 100 partidas de cada time
"""
import requests
import json
import time
from pathlib import Path
from datetime import datetime

API_KEY = '00495232-b2b4-4d0b-87e3-c01de846c4b4'
BASE = 'https://api.opendota.com/api'

# Times com IDs conhecidos
TEAMS = {
    'Team Falcons': 9247354,
    'Xtreme Gaming': 8599101,
    'Team Spirit': 7119388,
    'Team Liquid': 2163,
    'Tundra Esports': 8291895,
    'BetBoom Team': 8255888,
    'PARIVISION': 9824702,
    'HEROIC': 9303484,
    'Nigma Galaxy': 7554697,
    'OG': 2586976,
    'Aurora Gaming': 9467224,
    'Natus Vincere': 36,
    'Virtus.pro': 1883502,
    'MOUZ': 9338413
}

# Criar pasta de output
output_dir = Path('Database/Json/matches/dreamleague_s27')
output_dir.mkdir(parents=True, exist_ok=True)

print('=' * 70)
print('PROMETHEUS V7 - OpenDota Match Collector')
print('DreamLeague Season 27')
print('=' * 70)
print(f'API Key: Premium')
print(f'Times a coletar: {len(TEAMS)}')
print(f'Partidas por time: 100')
print('=' * 70)

all_teams_data = {}
total_matches = 0

for team_name, team_id in TEAMS.items():
    print(f'\n[{list(TEAMS.keys()).index(team_name)+1}/{len(TEAMS)}] {team_name} (ID: {team_id})')
    
    team_data = {
        'team_id': team_id,
        'team_name': team_name,
        'collected_at': datetime.now().isoformat(),
        'info': None,
        'players': [],
        'matches': [],
        'heroes': []
    }
    
    try:
        # 1. Info do time
        print(f'   - Buscando info do time...')
        r = requests.get(f'{BASE}/teams/{team_id}', params={'api_key': API_KEY}, timeout=30)
        if r.status_code == 200:
            team_data['info'] = r.json()
            print(f'     Rating: {team_data["info"].get("rating", "N/A")}')
        time.sleep(0.05)
        
        # 2. Jogadores do time
        print(f'   - Buscando jogadores...')
        r = requests.get(f'{BASE}/teams/{team_id}/players', params={'api_key': API_KEY}, timeout=30)
        if r.status_code == 200:
            players = r.json()
            # Filtrar jogadores atuais (com mais jogos recentes)
            current_players = sorted(players, key=lambda x: x.get('games_played', 0), reverse=True)[:10]
            team_data['players'] = current_players
            print(f'     Jogadores: {len(current_players)}')
        time.sleep(0.05)
        
        # 3. Últimas 100 partidas
        print(f'   - Buscando ultimas 100 partidas...')
        r = requests.get(f'{BASE}/teams/{team_id}/matches', params={'api_key': API_KEY, 'limit': 100}, timeout=30)
        if r.status_code == 200:
            matches = r.json()
            team_data['matches'] = matches
            total_matches += len(matches)
            print(f'     Partidas: {len(matches)}')
        time.sleep(0.05)
        
        # 4. Heróis do time
        print(f'   - Buscando herois...')
        r = requests.get(f'{BASE}/teams/{team_id}/heroes', params={'api_key': API_KEY}, timeout=30)
        if r.status_code == 200:
            heroes = r.json()[:30]  # Top 30 heróis
            team_data['heroes'] = heroes
            print(f'     Herois: {len(heroes)}')
        time.sleep(0.05)
        
        # Salvar arquivo do time
        filename = team_name.lower().replace(' ', '_').replace('.', '').replace('+', '_plus_')
        filepath = output_dir / f'{filename}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(team_data, f, indent=2, ensure_ascii=False)
        print(f'   [OK] Salvo: {filepath}')
        
        all_teams_data[team_name] = {
            'team_id': team_id,
            'matches_collected': len(team_data['matches']),
            'players_collected': len(team_data['players']),
            'filepath': str(filepath)
        }
        
    except Exception as e:
        print(f'   [ERRO] {e}')
        all_teams_data[team_name] = {'error': str(e)}

print('\n' + '=' * 70)
print('RESUMO DA COLETA')
print('=' * 70)
print(f'Times processados: {len(all_teams_data)}')
print(f'Total de partidas: {total_matches}')
print('=' * 70)

# Salvar índice
index_file = output_dir / '_index.json'
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump({
        'collected_at': datetime.now().isoformat(),
        'tournament': 'DreamLeague Season 27',
        'teams': all_teams_data,
        'total_matches': total_matches
    }, f, indent=2, ensure_ascii=False)

print(f'\nIndice salvo: {index_file}')
print('\nColeta finalizada!')
