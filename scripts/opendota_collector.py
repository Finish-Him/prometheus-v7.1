"""
OpenDota API Collector for DreamLeague Season 27
Prometheus V7 - Data Collection System

Este script coleta dados da API OpenDota para todos os times
participantes do DreamLeague S27, incluindo:
- Informações dos times
- Roster atual (jogadores ativos)
- Últimas 100 partidas por time
- Estatísticas dos jogadores

Author: Prometheus AI
Date: 2025-12-10
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
OPENDOTA_BASE_URL = "https://api.opendota.com/api"
API_KEY = "00495232-b2b4-4d0b-87e3-c01de846c4b4"  # 3000 req/min
RATE_LIMIT_DELAY = 0.1  # 100ms entre requests com API key

# Paths
BASE_PATH = Path(__file__).parent.parent
DATABASE_PATH = BASE_PATH / "Database" / "Json"
LEAGUES_PATH = DATABASE_PATH / "leagues"
TEAMS_PATH = DATABASE_PATH / "teams"
PLAYERS_PATH = DATABASE_PATH / "players"
MATCHES_PATH = DATABASE_PATH / "matches"


class OpenDotaCollector:
    """Coletor de dados da API OpenDota."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Prometheus-V7-Collector/1.0"
        })
        self.request_count = 0
        self.last_request_time = 0
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Faz uma requisição à API com rate limiting."""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        
        url = f"{OPENDOTA_BASE_URL}{endpoint}"
        params = params or {}
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            response = self.session.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            self.request_count += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit atingido, aguardando 60s...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"Erro {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Erro de conexão: {e}")
            return None
    
    # ==================== TEAM METHODS ====================
    
    def search_team(self, team_name: str) -> Optional[int]:
        """Busca o team_id pelo nome do time."""
        logger.info(f"Buscando team_id para: {team_name}")
        
        data = self._make_request("/search", {"q": team_name})
        if not data:
            return None
            
        # Filtra apenas times (não jogadores)
        teams = [item for item in data if item.get("similarity", 0) > 0.3]
        
        # Procura match exato ou mais próximo
        for item in teams:
            if item.get("name", "").lower() == team_name.lower():
                logger.info(f"✅ Encontrado: {item['name']} (ID: {item.get('id')})")
                return item.get("id")
        
        # Se não encontrou match exato, retorna o primeiro resultado relevante
        if teams:
            best = teams[0]
            logger.info(f"🔍 Melhor match: {best.get('name')} (ID: {best.get('id')})")
            return best.get("id")
            
        logger.warning(f"❌ Não encontrado: {team_name}")
        return None
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Obtém informações detalhadas de um time."""
        logger.info(f"Obtendo info do time {team_id}")
        return self._make_request(f"/teams/{team_id}")
    
    def get_team_players(self, team_id: int) -> List[Dict]:
        """Obtém a lista de jogadores de um time."""
        logger.info(f"Obtendo jogadores do time {team_id}")
        data = self._make_request(f"/teams/{team_id}/players")
        return data if data else []
    
    def get_team_matches(self, team_id: int, limit: int = 100) -> List[Dict]:
        """Obtém as últimas partidas de um time."""
        logger.info(f"Obtendo últimas {limit} partidas do time {team_id}")
        data = self._make_request(f"/teams/{team_id}/matches", {"limit": limit})
        return data if data else []
    
    def get_team_heroes(self, team_id: int) -> List[Dict]:
        """Obtém estatísticas de heróis de um time."""
        logger.info(f"Obtendo heróis do time {team_id}")
        data = self._make_request(f"/teams/{team_id}/heroes")
        return data if data else []
    
    # ==================== PLAYER METHODS ====================
    
    def get_player_info(self, account_id: int) -> Optional[Dict]:
        """Obtém informações de um jogador."""
        logger.info(f"Obtendo info do jogador {account_id}")
        return self._make_request(f"/players/{account_id}")
    
    def get_player_matches(self, account_id: int, limit: int = 100) -> List[Dict]:
        """Obtém as últimas partidas de um jogador."""
        logger.info(f"Obtendo últimas {limit} partidas do jogador {account_id}")
        data = self._make_request(f"/players/{account_id}/matches", {"limit": limit})
        return data if data else []
    
    def get_player_heroes(self, account_id: int) -> List[Dict]:
        """Obtém estatísticas de heróis de um jogador."""
        logger.info(f"Obtendo heróis do jogador {account_id}")
        data = self._make_request(f"/players/{account_id}/heroes")
        return data if data else []
    
    def get_player_totals(self, account_id: int) -> List[Dict]:
        """Obtém totais de um jogador (kills, deaths, etc)."""
        logger.info(f"Obtendo totais do jogador {account_id}")
        data = self._make_request(f"/players/{account_id}/totals")
        return data if data else []
    
    def get_player_wl(self, account_id: int) -> Optional[Dict]:
        """Obtém win/loss de um jogador."""
        return self._make_request(f"/players/{account_id}/wl")
    
    # ==================== UTILITY METHODS ====================
    
    def get_current_roster(self, team_id: int) -> List[Dict]:
        """Obtém apenas jogadores atuais do time."""
        players = self.get_team_players(team_id)
        
        # Filtrar por jogadores ativos (is_current_team_member ou jogos recentes)
        current = []
        for player in players:
            # Considera como atual se:
            # 1. is_current_team_member == True, ou
            # 2. Jogou nos últimos 30 dias
            if player.get("is_current_team_member"):
                current.append(player)
            elif player.get("last_match_time"):
                # Verifica se jogou recentemente
                last_match = datetime.fromtimestamp(player["last_match_time"])
                days_ago = (datetime.now() - last_match).days
                if days_ago <= 30 and player.get("games_played", 0) >= 10:
                    current.append(player)
        
        # Ordena por jogos jogados (mais jogos = mais relevante)
        current.sort(key=lambda x: x.get("games_played", 0), reverse=True)
        
        # Retorna apenas os 5 principais (roster padrão)
        return current[:5]


class DreamLeagueDataCollector:
    """Coletor específico para DreamLeague S27."""
    
    def __init__(self):
        self.collector = OpenDotaCollector()
        self.dreamleague_data = self._load_dreamleague_data()
        
    def _load_dreamleague_data(self) -> Dict:
        """Carrega dados atuais do DreamLeague S27."""
        filepath = LEAGUES_PATH / "dreamleague_s27.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_dreamleague_data(self):
        """Salva dados atualizados do DreamLeague S27."""
        filepath = LEAGUES_PATH / "dreamleague_s27.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.dreamleague_data, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Dados salvos em {filepath}")
    
    def resolve_all_team_ids(self) -> Dict[str, int]:
        """Resolve team_ids para todos os times que ainda não têm."""
        logger.info("=" * 50)
        logger.info("RESOLVENDO TEAM IDs")
        logger.info("=" * 50)
        
        resolved = {}
        teams = self.dreamleague_data.get("teams", [])
        
        for team in teams:
            team_name = team.get("name")
            current_id = team.get("team_id")
            
            if current_id:
                logger.info(f"✅ {team_name}: {current_id} (já conhecido)")
                resolved[team_name] = current_id
            else:
                # Tenta buscar na API
                team_id = self.collector.search_team(team_name)
                if team_id:
                    team["team_id"] = team_id
                    resolved[team_name] = team_id
                else:
                    # Tenta variações do nome
                    variations = [
                        team.get("tag"),
                        team_name.replace(" ", ""),
                        team_name.split()[0] if " " in team_name else None
                    ]
                    for var in filter(None, variations):
                        team_id = self.collector.search_team(var)
                        if team_id:
                            team["team_id"] = team_id
                            resolved[team_name] = team_id
                            break
        
        self._save_dreamleague_data()
        
        logger.info("=" * 50)
        logger.info(f"RESULTADO: {len(resolved)}/{len(teams)} times resolvidos")
        logger.info("=" * 50)
        
        return resolved
    
    def collect_team_data(self, team_id: int) -> Dict:
        """Coleta todos os dados de um time."""
        data = {
            "team_info": self.collector.get_team_info(team_id),
            "players": self.collector.get_current_roster(team_id),
            "matches": self.collector.get_team_matches(team_id, limit=100),
            "heroes": self.collector.get_team_heroes(team_id),
            "collected_at": datetime.now().isoformat()
        }
        return data
    
    def collect_player_data(self, account_id: int) -> Dict:
        """Coleta todos os dados de um jogador."""
        data = {
            "player_info": self.collector.get_player_info(account_id),
            "win_loss": self.collector.get_player_wl(account_id),
            "heroes": self.collector.get_player_heroes(account_id)[:20],  # Top 20 heróis
            "matches": self.collector.get_player_matches(account_id, limit=50),
            "collected_at": datetime.now().isoformat()
        }
        return data
    
    def collect_all_teams(self) -> Dict[str, Dict]:
        """Coleta dados de todos os times do torneio."""
        logger.info("=" * 50)
        logger.info("COLETANDO DADOS DE TODOS OS TIMES")
        logger.info("=" * 50)
        
        all_data = {}
        teams = self.dreamleague_data.get("teams", [])
        
        for i, team in enumerate(teams, 1):
            team_name = team.get("name")
            team_id = team.get("team_id")
            
            logger.info(f"\n[{i}/{len(teams)}] Coletando: {team_name}")
            
            if not team_id:
                logger.warning(f"⚠️ {team_name}: sem team_id, pulando...")
                continue
            
            try:
                team_data = self.collect_team_data(team_id)
                all_data[team_name] = team_data
                
                # Salva dados individuais do time
                self._save_team_data(team_name, team_data)
                
                logger.info(f"✅ {team_name}: {len(team_data.get('matches', []))} partidas coletadas")
                
            except Exception as e:
                logger.error(f"❌ Erro ao coletar {team_name}: {e}")
        
        logger.info("=" * 50)
        logger.info(f"COLETA FINALIZADA: {len(all_data)} times processados")
        logger.info(f"Total de requests: {self.collector.request_count}")
        logger.info("=" * 50)
        
        return all_data
    
    def _save_team_data(self, team_name: str, data: Dict):
        """Salva dados de um time em arquivo separado."""
        # Cria pasta se não existir
        team_folder = MATCHES_PATH / "dreamleague_s27"
        team_folder.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo (snake_case)
        filename = team_name.lower().replace(" ", "_").replace(".", "").replace("+", "_plus_")
        filepath = team_folder / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Salvo: {filepath}")
    
    def build_pro_teams_json(self) -> Dict:
        """Constrói o arquivo pro_teams.json com dados coletados."""
        logger.info("Construindo pro_teams.json...")
        
        pro_teams = {
            "$schema": "prometheus_teams_v2",
            "version": "2.0.0",
            "last_updated": datetime.now().isoformat(),
            "tournament": "dreamleague_s27",
            "teams": []
        }
        
        teams_folder = MATCHES_PATH / "dreamleague_s27"
        if not teams_folder.exists():
            logger.error("Pasta de times não existe!")
            return pro_teams
        
        for filepath in teams_folder.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            team_info = data.get("team_info", {})
            players = data.get("players", [])
            matches = data.get("matches", [])
            
            if not team_info:
                continue
            
            # Calcula estatísticas
            total_matches = len(matches)
            wins = sum(1 for m in matches if m.get("radiant_win") == m.get("radiant"))
            winrate = (wins / total_matches * 100) if total_matches > 0 else 0
            
            team_entry = {
                "team_id": team_info.get("team_id"),
                "name": team_info.get("name"),
                "tag": team_info.get("tag"),
                "rating": team_info.get("rating"),
                "wins": team_info.get("wins"),
                "losses": team_info.get("losses"),
                "last_match_time": team_info.get("last_match_time"),
                "current_roster": [
                    {
                        "account_id": p.get("account_id"),
                        "name": p.get("name"),
                        "games_played": p.get("games_played"),
                        "wins": p.get("wins"),
                        "is_current": p.get("is_current_team_member", False)
                    }
                    for p in players[:5]
                ],
                "stats": {
                    "recent_matches": total_matches,
                    "recent_winrate": round(winrate, 1),
                    "avg_duration": sum(m.get("duration", 0) for m in matches) // max(len(matches), 1)
                }
            }
            
            pro_teams["teams"].append(team_entry)
        
        # Salva arquivo
        filepath = TEAMS_PATH / "pro_teams.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pro_teams, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ pro_teams.json salvo com {len(pro_teams['teams'])} times")
        return pro_teams
    
    def build_pro_players_json(self) -> Dict:
        """Constrói o arquivo pro_players.json com dados coletados."""
        logger.info("Construindo pro_players.json...")
        
        pro_players = {
            "$schema": "prometheus_players_v2",
            "version": "2.0.0",
            "last_updated": datetime.now().isoformat(),
            "tournament": "dreamleague_s27",
            "players": []
        }
        
        teams_folder = MATCHES_PATH / "dreamleague_s27"
        if not teams_folder.exists():
            return pro_players
        
        for filepath in teams_folder.glob("*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            team_info = data.get("team_info", {})
            players = data.get("players", [])
            
            for player in players[:5]:  # Top 5 jogadores
                player_entry = {
                    "account_id": player.get("account_id"),
                    "name": player.get("name"),
                    "team_id": team_info.get("team_id"),
                    "team_name": team_info.get("name"),
                    "games_played": player.get("games_played"),
                    "wins": player.get("wins"),
                    "winrate": round(player.get("wins", 0) / max(player.get("games_played", 1), 1) * 100, 1),
                    "is_current_team_member": player.get("is_current_team_member", False)
                }
                pro_players["players"].append(player_entry)
        
        # Salva arquivo
        filepath = PLAYERS_PATH / "pro_players.json"
        PLAYERS_PATH.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pro_players, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ pro_players.json salvo com {len(pro_players['players'])} jogadores")
        return pro_players


def main():
    """Função principal de coleta."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         PROMETHEUS V7 - OpenDota Data Collector              ║
    ║              DreamLeague Season 27 Edition                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    collector = DreamLeagueDataCollector()
    
    # Menu de opções
    print("\nOpções disponíveis:")
    print("1. Resolver Team IDs faltantes")
    print("2. Coletar dados de todos os times")
    print("3. Construir pro_teams.json")
    print("4. Construir pro_players.json")
    print("5. Executar tudo (pipeline completo)")
    print("0. Sair")
    
    choice = input("\nEscolha uma opção: ").strip()
    
    if choice == "1":
        collector.resolve_all_team_ids()
    elif choice == "2":
        collector.collect_all_teams()
    elif choice == "3":
        collector.build_pro_teams_json()
    elif choice == "4":
        collector.build_pro_players_json()
    elif choice == "5":
        logger.info("Executando pipeline completo...")
        collector.resolve_all_team_ids()
        collector.collect_all_teams()
        collector.build_pro_teams_json()
        collector.build_pro_players_json()
        logger.info("Pipeline completo finalizado!")
    elif choice == "0":
        print("Saindo...")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()
