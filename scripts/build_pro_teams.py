"""
Build Pro Teams JSON - Consolidar dados coletados
"""
import json
from pathlib import Path
from datetime import datetime

MATCHES_DIR = Path('Database/Json/matches/dreamleague_s27')
OUTPUT_FILE = Path('Database/Json/teams/pro_teams.json')

print('=' * 60)
print('PROMETHEUS V7 - Building pro_teams.json')
print('=' * 60)

pro_teams = {
    "$schema": "prometheus_teams_v2",
    "version": "2.0.0",
    "last_updated": datetime.now().isoformat(),
    "tournament": "dreamleague_s27",
    "teams": []
}

for filepath in sorted(MATCHES_DIR.glob('*.json')):
    if filepath.name.startswith('_'):
        continue
    
    print(f'Processando: {filepath.name}')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    info = data.get('info', {})
    players = data.get('players', [])
    matches = data.get('matches', [])
    heroes = data.get('heroes', [])
    
    if not info:
        continue
    
    # Calcular estatísticas das últimas 100 partidas
    recent_matches = matches[:100] if len(matches) >= 100 else matches
    wins = sum(1 for m in recent_matches if m.get('radiant_win') == m.get('radiant'))
    total = len(recent_matches)
    winrate = (wins / total * 100) if total > 0 else 0
    avg_duration = sum(m.get('duration', 0) for m in recent_matches) // max(total, 1)
    
    # Filtrar jogadores atuais (top 5 por jogos)
    current_roster = []
    for p in sorted(players, key=lambda x: x.get('games_played', 0), reverse=True)[:5]:
        current_roster.append({
            "account_id": p.get('account_id'),
            "name": p.get('name'),
            "games_played": p.get('games_played'),
            "wins": p.get('wins'),
            "winrate": round(p.get('wins', 0) / max(p.get('games_played', 1), 1) * 100, 1)
        })
    
    # Top 5 heróis
    top_heroes = []
    for h in sorted(heroes, key=lambda x: x.get('games_played', 0), reverse=True)[:5]:
        top_heroes.append({
            "hero_id": h.get('hero_id'),
            "games": h.get('games_played'),
            "wins": h.get('wins'),
            "winrate": round(h.get('wins', 0) / max(h.get('games_played', 1), 1) * 100, 1)
        })
    
    team_entry = {
        "team_id": info.get('team_id'),
        "name": info.get('name'),
        "tag": info.get('tag'),
        "logo_url": info.get('logo_url'),
        "rating": info.get('rating'),
        "all_time_wins": info.get('wins'),
        "all_time_losses": info.get('losses'),
        "last_match_time": info.get('last_match_time'),
        "current_roster": current_roster,
        "recent_stats": {
            "matches": total,
            "wins": wins,
            "losses": total - wins,
            "winrate": round(winrate, 1),
            "avg_duration_sec": avg_duration,
            "avg_duration_min": round(avg_duration / 60, 1)
        },
        "top_heroes": top_heroes
    }
    
    pro_teams['teams'].append(team_entry)
    print(f'  -> {info.get("name")}: {total} matches, {winrate:.1f}% WR')

# Ordenar por rating
pro_teams['teams'].sort(key=lambda x: x.get('rating', 0), reverse=True)

# Salvar
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(pro_teams, f, indent=2, ensure_ascii=False)

print('\n' + '=' * 60)
print(f'Salvo: {OUTPUT_FILE}')
print(f'Total: {len(pro_teams["teams"])} times')
print('=' * 60)
