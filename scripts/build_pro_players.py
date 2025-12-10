"""
Build Pro Players JSON - Consolidar dados de jogadores
"""
import json
from pathlib import Path
from datetime import datetime

MATCHES_DIR = Path('Database/Json/matches/dreamleague_s27')
OUTPUT_FILE = Path('Database/Json/players/pro_players.json')

print('=' * 60)
print('PROMETHEUS V7 - Building pro_players.json')
print('=' * 60)

pro_players = {
    "$schema": "prometheus_players_v2",
    "version": "2.0.0",
    "last_updated": datetime.now().isoformat(),
    "tournament": "dreamleague_s27",
    "players": []
}

for filepath in sorted(MATCHES_DIR.glob('*.json')):
    if filepath.name.startswith('_'):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    info = data.get('info', {})
    players = data.get('players', [])
    
    team_name = info.get('name', 'Unknown')
    team_id = info.get('team_id')
    
    print(f'{team_name}:')
    
    # Top 5 jogadores por jogos
    for i, p in enumerate(sorted(players, key=lambda x: x.get('games_played', 0), reverse=True)[:5], 1):
        games = p.get('games_played', 0)
        wins = p.get('wins', 0)
        winrate = (wins / games * 100) if games > 0 else 0
        
        player_entry = {
            "account_id": p.get('account_id'),
            "name": p.get('name'),
            "team_id": team_id,
            "team_name": team_name,
            "games_played": games,
            "wins": wins,
            "losses": games - wins,
            "winrate": round(winrate, 1),
            "is_current_team_member": p.get('is_current_team_member', False)
        }
        
        pro_players['players'].append(player_entry)
        status = "[ATUAL]" if p.get('is_current_team_member') else ""
        print(f'  {i}. {p.get("name", "Unknown")}: {games} jogos, {winrate:.1f}% WR {status}')

# Ordenar por winrate
pro_players['players'].sort(key=lambda x: (x.get('winrate', 0), x.get('games_played', 0)), reverse=True)

# Salvar
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(pro_players, f, indent=2, ensure_ascii=False)

print('\n' + '=' * 60)
print(f'Salvo: {OUTPUT_FILE}')
print(f'Total: {len(pro_players["players"])} jogadores')
print('=' * 60)
