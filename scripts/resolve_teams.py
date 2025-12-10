"""
Quick Team ID Resolver - OpenDota API
"""
import requests
import json
import time

API_KEY = '00495232-b2b4-4d0b-87e3-c01de846c4b4'
BASE = 'https://api.opendota.com/api'

teams_to_find = [
    ('Team Falcons', 'Falcons'),
    ('BetBoom Team', 'BetBoom'),
    ('PARIVISION', 'PARIVISION'),
    ('HEROIC', 'HEROIC'),
    ('Aurora Gaming', 'Aurora'),
    ('MOUZ', 'MOUZ'),
    ('GamerLegion', 'GamerLegion'),
    ('Amaru Gaming', 'Amaru'),
    ('Runa Team', 'Runa'),
    ('Yakult Brothers', 'Yakult'),
    ('Team Nemesis', 'Nemesis'),
    ('Team Yandex', 'Yandex'),
    ('1win Team', '1win'),
    ('Pipsqueak+4', 'Pipsqueak'),
    ('Passion UA', 'Passion'),
    ('Team Tidebound', 'Tidebound')
]

print('=' * 60)
print('PROMETHEUS V7 - OpenDota Team ID Resolver')
print('API Key: Premium (3000 req/min)')
print('=' * 60)

found = {}
not_found = []

for full_name, search_term in teams_to_find:
    try:
        r = requests.get(f'{BASE}/search', params={'q': search_term, 'api_key': API_KEY}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                best = data[0]
                team_id = best.get('id')
                team_name = best.get('name')
                print(f'[OK] {full_name}: {team_name} (ID: {team_id})')
                found[full_name] = {'id': team_id, 'name': team_name}
            else:
                print(f'[--] {full_name}: nao encontrado')
                not_found.append(full_name)
        else:
            print(f'[ER] {full_name}: HTTP {r.status_code}')
            not_found.append(full_name)
        time.sleep(0.1)  # Rate limit
    except Exception as e:
        print(f'[ER] {full_name}: {e}')
        not_found.append(full_name)

print('=' * 60)
print(f'Encontrados: {len(found)}/{len(teams_to_find)}')
print('=' * 60)

# Salvar resultado
with open('team_ids_resolved.json', 'w') as f:
    json.dump(found, f, indent=2)

print('Salvo em team_ids_resolved.json')
