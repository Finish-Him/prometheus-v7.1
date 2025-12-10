"""
Prometheus V7 - Main Entry Point for Streamlit Cloud
DreamLeague Season 27 Edition
"""
import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to import database module, fallback to JSON loading
try:
    from database import (
        load_dreamleague, load_pro_teams, load_pro_players,
        load_bets, save_bet, is_supabase_connected, get_data_source,
        clear_all_caches
    )
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

# Page Config
st.set_page_config(
    page_title="Prometheus V7 - Dota 2 Analytics",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
DATABASE_PATH = Path(__file__).parent / "Database" / "Json"

def load_json(filepath):
    """Load JSON file safely."""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
    return {}

# Wrapper functions for backward compatibility
def _load_dreamleague():
    """Load DreamLeague data with fallback to JSON."""
    data = None
    
    if USE_DATABASE:
        try:
            data = load_dreamleague()
        except:
            pass
    
    # Fallback to JSON if no schedule data
    if not data or not data.get("schedule"):
        data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s27.json")
    
    if not data or not data.get("schedule"):
        data = load_json(DATABASE_PATH / "leagues" / "dreamleague_s26.json")
    
    return data if data else {}

def _load_pro_teams():
    if USE_DATABASE:
        return load_pro_teams()
    return load_json(DATABASE_PATH / "teams" / "pro_teams.json")

def _load_pro_players():
    if USE_DATABASE:
        return load_pro_players()
    return load_json(DATABASE_PATH / "players" / "pro_players.json")

def _load_bets():
    if USE_DATABASE:
        return load_bets()
    data = load_json(DATABASE_PATH / "bets" / "user_bets.json")
    return data if data else {"bankroll": 1000, "bets": []}

def load_events():
    """Load upcoming events."""
    data = load_json(DATABASE_PATH / "events" / "upcoming.json")
    return data.get("events", [])

def main():
    # Sidebar
    st.sidebar.title("🔥 Prometheus V7")
    st.sidebar.caption("Dota 2 Betting Analytics")
    
    page = st.sidebar.radio(
        "Navegação",
        ["🏠 Dashboard", "🏆 DreamLeague S27", "💰 Apostas"]
        # Hidden pages (uncomment to enable):
        # "🎯 Match Hub", "👥 Pro Teams", "🎮 Pro Players", "📊 Analytics 2025", "📅 Eventos"
    )
    
    st.sidebar.markdown("---")
    
    # Live clock GMT-3 (São Paulo)
    import pytz
    sp_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sp_tz)
    st.sidebar.markdown(f"### 🕐 {current_time.strftime('%H:%M:%S')}")
    st.sidebar.caption(f"📅 {current_time.strftime('%d/%m/%Y')} (GMT-3)")
    
    st.sidebar.markdown("---")
    
    # Data source indicator
    if USE_DATABASE:
        st.sidebar.caption(f"📊 {get_data_source()}")
    else:
        st.sidebar.caption("📊 🟡 JSON (Local)")
    
    st.sidebar.caption("🔗 Data: OpenDota API + Steam")
    
    # Refresh button
    if USE_DATABASE:
        if st.sidebar.button("🔄 Atualizar Dados"):
            clear_all_caches()
            st.rerun()
    
    # Main Content
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "🎯 Match Hub":
        render_match_hub()
    elif page == "🏆 DreamLeague S27":
        render_dreamleague()
    elif page == "👥 Pro Teams":
        render_pro_teams()
    elif page == "🎮 Pro Players":
        render_pro_players()
    elif page == "📊 Analytics 2025":
        render_analytics_2025()
    elif page == "📅 Eventos":
        render_events()
    elif page == "💰 Apostas":
        render_bets()

def render_dashboard():
    """Render main dashboard - Mobile-first design."""
    import pytz
    sp_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sp_tz)
    
    # Mobile-optimized CSS
    st.markdown("""
    <style>
    .match-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #444;
    }
    .match-card.live { border-left-color: #ff4444; }
    .match-card.soon { border-left-color: #ffaa00; }
    .match-card.upcoming { border-left-color: #44ff44; }
    .match-time { font-size: 12px; color: #888; }
    .match-teams { font-size: 16px; font-weight: bold; text-align: center; padding: 8px 0; }
    .match-status { font-weight: bold; }
    .status-live { color: #ff4444; }
    .status-soon { color: #ffaa00; }
    .status-ok { color: #44ff44; }
    .team-card {
        background: #1a1a2e;
        padding: 10px 12px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .metric-box {
        background: #16213e;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #fff; }
    .metric-label { font-size: 12px; color: #888; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header compacto
    st.markdown(f"""
    <div style='text-align: center; padding: 5px 0;'>
        <h2 style='margin: 0;'>🔥 Prometheus</h2>
        <p style='margin: 5px 0; color: #888;'>⏰ {current_time.strftime('%H:%M')} BRT | 📅 {current_time.strftime('%d/%m')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Atualizar", use_container_width=True):
        st.rerun()
    
    # Load data
    bets = _load_bets()
    dl = _load_dreamleague()
    schedule = dl.get("schedule", {})
    teams = dl.get("teams", [])
    tournament = dl.get("tournament", {})
    
    # Métricas compactas (2x2 grid)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💵 Banca", f"R$ {bets.get('bankroll', 1000):.0f}")
    with col2:
        active = len([b for b in bets.get("bets", []) if b.get("status") == "pending"])
        st.metric("🎯 Apostas", active)
    
    col1, col2 = st.columns(2)
    with col1:
        prize = tournament.get('prize_pool', 1000000)
        st.metric("💰 Prize", f"${prize/1000:.0f}K")
    with col2:
        st.metric("🎮 Times", len(teams))
    
    st.markdown("---")
    
    # PARTIDAS - Cards visuais
    st.markdown("### 📅 Partidas de Hoje")
    
    round_1 = schedule.get("round_1", {}).get("matches", [])
    
    if round_1:
        for match in round_1[:8]:
            time_str = match.get('time_brt', '12:00')
            if len(time_str) > 5:
                time_str = time_str[:5]
            
            team_a = match.get('team_a', 'TBD')
            team_b = match.get('team_b', 'TBD')
            match_format = match.get('format', 'Bo3')
            
            # Countdown
            try:
                match_time = datetime.strptime(f"2025-12-10 {time_str}", "%Y-%m-%d %H:%M")
                match_time = sp_tz.localize(match_time)
                hours = (match_time - current_time).total_seconds() / 3600
            except:
                hours = 99
            
            if hours <= 0:
                status = "🔴 LIVE"
                card_class = "live"
                status_class = "status-live"
            elif hours <= 1:
                status = f"⚠️ {int(hours*60)}min"
                card_class = "soon"
                status_class = "status-soon"
            elif hours <= 2:
                status = f"🟡 {hours:.1f}h"
                card_class = "soon"
                status_class = "status-soon"
            else:
                status = f"🟢 {hours:.1f}h"
                card_class = "upcoming"
                status_class = "status-ok"
            
            # Card visual
            st.markdown(f"""
            <div class='match-card {card_class}'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span class='match-time'>🕐 {time_str}</span>
                    <span class='match-status {status_class}'>{status}</span>
                </div>
                <div class='match-teams'>
                    {team_a} <span style='color: #666; padding: 0 8px;'>vs</span> {team_b}
                </div>
                <div style='text-align: center; font-size: 11px; color: #666;'>{match_format}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 Nenhuma partida agendada")
    
    st.markdown("---")
    
    # TOP TEAMS - Compacto
    st.markdown("### ⭐ Favoritos")
    
    tier_s = [t for t in teams if t.get("tier") in ["S", "A"]][:6]
    
    for team in tier_s:
        roster = team.get("roster", [])
        players = ", ".join([p.get("name", "") for p in roster[:3]]) if roster else "N/A"
        
        st.markdown(f"""
        <div class='team-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-weight: bold;'>🏆 {team.get("name")}</span>
                <span style='color: #888; font-size: 12px;'>#{team.get("ranking", "?")} {team.get("region", "")}</span>
            </div>
            <div style='font-size: 11px; color: #666; margin-top: 4px;'>
                ⚔️ {players}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Links rápidos
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🟣 Twitch", "https://twitch.tv/dreamleague", use_container_width=True)
    with col2:
        st.link_button("🔴 YouTube", "https://youtube.com/dreamleague", use_container_width=True)

def render_dreamleague():
    """Render DreamLeague S27 page - Mobile-optimized."""
    import pytz
    sp_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sp_tz)
    
    # Mobile header
    st.markdown(f"""
    <div style='text-align: center;'>
        <h2>🏆 DreamLeague S27</h2>
        <p style='color: #888;'>Stockholm | 09-20 Dez | $1M Prize</p>
    </div>
    """, unsafe_allow_html=True)
    
    data = _load_dreamleague()
    pro_teams = _load_pro_teams()
    
    if not data:
        st.error("❌ Dados não carregados")
        return
    
    tournament = data.get("tournament", {})
    teams = data.get("teams", [])
    schedule = data.get("schedule", {})
    
    # Import modules
    try:
        from notifications import get_hours_until_match, format_countdown, get_countdown_color
        from odds_tracker import get_tracker, calculate_kelly
        from draft_analyzer import analyze_draft, analyze_single_draft
        MODULES_AVAILABLE = True
    except ImportError:
        MODULES_AVAILABLE = False
    
    # Métricas compactas mobile
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎮 Times", len(teams))
    with col2:
        st.metric("⏰ Agora", current_time.strftime('%H:%M'))
    
    # Tabs simplificadas
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Partidas", "👥 Times", "💰 Odds", "🎯 Draft"])
    
    # TAB 1 - PARTIDAS (Mobile cards)
    with tab1:
        round_1 = schedule.get("round_1", {}).get("matches", [])
        
        if not round_1:
            st.info("📭 Nenhuma partida")
        else:
            for match in round_1[:10]:
                time_str = match.get('time_brt', '12:00')
                if len(time_str) > 5:
                    time_str = time_str[:5]
                
                team_a = match.get("team_a", "TBD")
                team_b = match.get("team_b", "TBD")
                
                # Countdown
                try:
                    match_time = datetime.strptime(f"2025-12-10 {time_str}", "%Y-%m-%d %H:%M")
                    match_time = sp_tz.localize(match_time)
                    hours = (match_time - current_time).total_seconds() / 3600
                except:
                    hours = 99
                
                if hours <= 0:
                    status = "🔴 LIVE"
                    border = "#ff4444"
                elif hours <= 2:
                    status = f"⚠️ {int(hours*60)}min" if hours < 1 else f"🟡 {hours:.1f}h"
                    border = "#ffaa00"
                else:
                    status = f"🟢 {hours:.1f}h"
                    border = "#44ff44"
                
                st.markdown(f"""
                <div style='background: #1a1a2e; padding: 12px; border-radius: 8px; 
                            margin: 6px 0; border-left: 3px solid {border};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='font-size: 12px; color: #888;'>🕐 {time_str}</span>
                        <span style='font-weight: bold; color: {border};'>{status}</span>
                    </div>
                    <div style='text-align: center; padding: 8px 0; font-size: 15px;'>
                        <b>{team_a}</b> <span style='color: #666;'>vs</span> <b>{team_b}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # TAB 2 - TIMES (Mobile cards)
    with tab2:
        st.markdown("### 👥 Times")
        
        pro_map = {t.get("team_id"): t for t in pro_teams.get("teams", [])}
        tier_filter = st.selectbox("Tier", ["Todos", "S", "A", "B", "C"], key="tier_dl")
        
        for team in teams:
            tier = team.get("tier", "C")
            if tier_filter != "Todos" and tier != tier_filter:
                continue
            
            tier_color = {"S": "#9b59b6", "A": "#3498db", "B": "#2ecc71", "C": "#95a5a6"}.get(tier, "#95a5a6")
            pro_data = pro_map.get(team.get("team_id"), {})
            recent = pro_data.get("recent_stats", {}) if pro_data else {}
            
            st.markdown(f"""
            <div style='background: #1a1a2e; padding: 12px; border-radius: 8px; 
                        margin: 6px 0; border-left: 3px solid {tier_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: bold;'>{team.get('name')}</span>
                    <span style='background: {tier_color}; padding: 2px 8px; border-radius: 4px; 
                                 font-size: 11px;'>Tier {tier}</span>
                </div>
                <div style='font-size: 12px; color: #888; margin-top: 4px;'>
                    {team.get('region', 'EU')} • WR: {recent.get('winrate', 'N/A')}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"👥 {team.get('tag', '')} Roster"):
                for i, player in enumerate(team.get("roster", [])[:5]):
                    role = ["Carry", "Mid", "Offlane", "Soft", "Hard"][i] if i < 5 else "Sub"
                    st.write(f"**{i+1}.** {player.get('name')} - {role}")
    
    # TAB 3 - ODDS (Mobile)
    with tab3:
        st.markdown("### 💰 Odds")
        
        team_names = [t.get("name") for t in teams]
        
        t_a = st.selectbox("Time A", team_names, key="odds_a")
        odd_a = st.number_input("Odd A", min_value=1.01, value=1.50, key="val_a")
        
        t_b = st.selectbox("Time B", [t for t in team_names if t != t_a], key="odds_b")
        odd_b = st.number_input("Odd B", min_value=1.01, value=2.50, key="val_b")
        
        bookie = st.selectbox("Casa", ["bet365", "Betano", "Pinnacle", "Stake"], key="bm")
        
        if st.button("💾 Salvar"):
            st.success(f"✅ {t_a} @{odd_a} vs {t_b} @{odd_b}")
        
        st.markdown("---")
        st.markdown("##### 🎯 Value Calc")
        
        col1, col2 = st.columns(2)
        with col1:
            prob = st.slider("Prob %", 0, 100, 55, key="prob_c")
        with col2:
            odd = st.number_input("Odd", min_value=1.01, value=1.80, key="odd_c")
        
        implied = 100 / odd
        value = prob - implied
        if value > 0:
            st.success(f"✅ VALUE +{value:.1f}%")
        else:
            st.error(f"❌ No Value {value:.1f}%")
    
    # TAB 4 - DRAFT (Mobile)
    with tab4:
        st.markdown("### 🎯 Draft")
        
        heroes = ["Faceless Void", "Phantom Assassin", "Morphling", "Invoker", "Storm Spirit",
                  "Mars", "Axe", "Tidehunter", "Crystal Maiden", "Lion",
                  "Earth Spirit", "Tusk", "Rubick", "Snapfire", "Marci"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Radiant**")
            rad = [st.selectbox(f"R{i+1}", heroes, key=f"r{i}", index=i%len(heroes)) for i in range(5)]
        with col2:
            st.markdown("**Dire**")
            dire = [st.selectbox(f"D{i+1}", heroes, key=f"d{i}", index=(i+5)%len(heroes)) for i in range(5)]
        
        if st.button("🔍 Analisar"):
            if MODULES_AVAILABLE:
                analysis = analyze_draft(rad, dire)
                winner = analysis.get("predicted_winner", "Even")
                prob = analysis.get("win_probability", {})
                st.markdown(f"""
                <div style='background: #1a1a2e; padding: 15px; border-radius: 8px; text-align: center;'>
                    <div style='font-size: 18px; margin-bottom: 8px;'>🏆 {winner}</div>
                    <div style='font-size: 14px; color: #888;'>
                        Radiant {prob.get('radiant', 50)}% | Dire {prob.get('dire', 50)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Draft Analyzer: Disponível em breve")


def render_pro_teams():
    """Render Pro Teams page."""
    st.title("👥 Pro Teams - OpenDota Data")
    
    pro_teams = _load_pro_teams()
    teams = pro_teams.get("teams", [])
    
    st.caption(f"📅 Atualização: {pro_teams.get('last_updated', 'N/A')[:10]}")
    st.caption(f"📊 Total: {len(teams)} times | 🔗 Fonte: OpenDota API")
    
    st.markdown("---")
    
    for team in teams:
        recent = team.get("recent_stats", {})
        roster = team.get("current_roster", [])
        heroes = team.get("top_heroes", [])
        
        with st.expander(f"**{team.get('name')}** ({team.get('tag')}) - ⭐ {team.get('rating', 0):.0f}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📈 Win Rate (100g)", f"{recent.get('winrate', 0)}%")
                st.metric("🎮 Partidas", recent.get("matches", 0))
            
            with col2:
                st.metric("✅ Vitórias", recent.get("wins", 0))
                st.metric("❌ Derrotas", recent.get("losses", 0))
            
            with col3:
                st.metric("⏱️ Duração Média", f"{recent.get('avg_duration_min', 0)} min")
                st.metric("🏆 All-Time Wins", team.get("all_time_wins", 0))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🎮 Roster:**")
                for p in roster[:5]:
                    wr = p.get("winrate", 0)
                    st.write(f"• {p.get('name')} - {p.get('games_played')} jogos ({wr}% WR)")
            
            with col2:
                st.write("**🦸 Top Heróis:**")
                for h in heroes[:5]:
                    st.write(f"• Hero {h.get('hero_id')}: {h.get('games')} jogos ({h.get('winrate')}% WR)")

def render_pro_players():
    """Render Pro Players page."""
    st.title("🎮 Pro Players - OpenDota Data")
    
    pro_players = _load_pro_players()
    players = pro_players.get("players", [])
    
    st.caption(f"📅 Atualização: {pro_players.get('last_updated', 'N/A')[:10]}")
    st.caption(f"📊 Total: {len(players)} jogadores")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        teams_list = list(set(p.get("team_name") for p in players if p.get("team_name")))
        team_filter = st.selectbox("Filtrar por Time", ["Todos"] + sorted(teams_list))
    with col2:
        sort_by = st.selectbox("Ordenar por", ["Win Rate", "Jogos", "Nome"])
    
    filtered = players
    if team_filter != "Todos":
        filtered = [p for p in players if p.get("team_name") == team_filter]
    
    if sort_by == "Win Rate":
        filtered = sorted(filtered, key=lambda x: x.get("winrate", 0), reverse=True)
    elif sort_by == "Jogos":
        filtered = sorted(filtered, key=lambda x: x.get("games_played", 0), reverse=True)
    else:
        filtered = sorted(filtered, key=lambda x: x.get("name", ""))
    
    for player in filtered[:30]:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            status = "🟢" if player.get("is_current_team_member") else "⚪"
            st.write(f"{status} **{player.get('name', 'Unknown')}**")
        
        with col2:
            st.write(player.get("team_name", "N/A"))
        
        with col3:
            st.write(f"{player.get('games_played', 0)} jogos")
        
        with col4:
            wr = player.get("winrate", 0)
            color = "🟢" if wr >= 55 else "🟡" if wr >= 50 else "🔴"
            st.write(f"{color} {wr}%")

def render_events():
    """Render events page."""
    st.title("📅 Próximos Eventos")
    
    events = load_events()
    
    if not events:
        st.info("Nenhum evento carregado.")
        return
    
    for event in events[:10]:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.caption(event.get("date", "TBD"))
                st.write(f"🕐 {event.get('time', 'TBD')}")
            
            with col2:
                st.write(f"**{event.get('team_a', 'TBD')}** vs **{event.get('team_b', 'TBD')}**")
                st.caption(event.get("league", "")[:50])
            
            with col3:
                st.write(f"📋 {event.get('format', 'Bo3')}")
            
            st.markdown("---")

def render_bets():
    """Render bets management page - Complete betting tracker."""
    st.title("💰 Gestão de Apostas")
    
    import pytz
    sp_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sp_tz)
    
    bets_data = _load_bets()
    dl = _load_dreamleague()
    teams = dl.get("teams", [])
    schedule = dl.get("schedule", {})
    
    # Try to import modules
    try:
        from odds_tracker import calculate_kelly
        CALC_AVAILABLE = True
    except:
        CALC_AVAILABLE = False
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    bankroll = bets_data.get('bankroll', 1000)
    all_bets = bets_data.get("bets", [])
    pending = [b for b in all_bets if b.get("status") == "pending"]
    won = [b for b in all_bets if b.get("status") == "won"]
    lost = [b for b in all_bets if b.get("status") == "lost"]
    
    with col1:
        st.metric("💵 Banca Atual", f"R$ {bankroll:.2f}")
    with col2:
        st.metric("🎯 Pendentes", len(pending))
    with col3:
        st.metric("✅ Ganhas", len(won))
    with col4:
        st.metric("❌ Perdidas", len(lost))
    
    # Calculate P/L
    total_won = sum(b.get("profit", 0) for b in won)
    total_lost = sum(b.get("stake", 0) for b in lost)
    net_pl = total_won - total_lost
    
    if net_pl >= 0:
        st.success(f"📈 Lucro Total: **R$ {net_pl:.2f}**")
    else:
        st.error(f"📉 Prejuízo Total: **R$ {abs(net_pl):.2f}**")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Nova Aposta", "📋 Apostas Ativas", "📊 Histórico", "🧮 Calculadora"])
    
    # TAB 1 - NOVA APOSTA
    with tab1:
        st.subheader("➕ Registrar Nova Aposta")
        
        # Get upcoming matches for quick selection
        round_1 = schedule.get("round_1", {}).get("matches", [])
        match_options = [f"{m.get('team_a')} vs {m.get('team_b')}" for m in round_1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📅 Partida")
            
            if match_options:
                selected_match = st.selectbox("Selecionar Partida", ["Personalizado"] + match_options)
                
                if selected_match != "Personalizado":
                    parts = selected_match.split(" vs ")
                    team_a = parts[0]
                    team_b = parts[1] if len(parts) > 1 else ""
                else:
                    team_names = [t.get("name") for t in teams]
                    team_a = st.selectbox("Time A", team_names)
                    team_b = st.selectbox("Time B", [t for t in team_names if t != team_a])
            else:
                team_names = [t.get("name") for t in teams]
                team_a = st.selectbox("Time A", team_names)
                team_b = st.selectbox("Time B", [t for t in team_names if t != team_a])
            
            selection = st.radio("🎯 Apostar em:", [team_a, team_b])
        
        with col2:
            st.markdown("##### 💰 Valores")
            
            odds = st.number_input("Odd", min_value=1.01, max_value=50.0, value=1.80, step=0.01)
            
            # Stake options
            stake_type = st.radio("Tipo de Stake", ["Valor Fixo", "% da Banca", "Kelly"])
            
            if stake_type == "Valor Fixo":
                stake = st.number_input("Valor (R$)", min_value=10.0, max_value=bankroll, value=50.0, step=10.0)
            elif stake_type == "% da Banca":
                pct = st.slider("% da Banca", 1, 20, 5)
                stake = bankroll * (pct / 100)
                st.info(f"Stake: R$ {stake:.2f}")
            else:
                prob = st.slider("Sua probabilidade (%)", 30, 90, 55)
                if CALC_AVAILABLE:
                    kelly_pct = calculate_kelly(prob, odds)
                else:
                    kelly_pct = max(0, (prob * odds - 100) / (odds - 1)) / 100 * 100
                kelly_pct = min(kelly_pct, 10)  # Cap at 10%
                stake = bankroll * (kelly_pct / 100)
                st.info(f"Kelly: {kelly_pct:.1f}% = R$ {stake:.2f}")
            
            bookmaker = st.selectbox("Casa", ["bet365", "Betano", "Betfair", "Pinnacle", "1xBet", "Rivalry", "GG.bet", "Stake"])
        
        # Preview
        st.markdown("---")
        potential = stake * odds
        profit = potential - stake
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Stake", f"R$ {stake:.2f}")
        with col2:
            st.metric("🎯 Retorno", f"R$ {potential:.2f}")
        with col3:
            st.metric("📈 Lucro", f"R$ {profit:.2f}")
        
        if st.button("✅ Registrar Aposta", type="primary"):
            new_bet = {
                "id": f"bet_{len(all_bets)+1}_{current_time.strftime('%Y%m%d%H%M')}",
                "match": f"{team_a} vs {team_b}",
                "selection": selection,
                "odds": odds,
                "stake": stake,
                "potential": potential,
                "bookmaker": bookmaker,
                "status": "pending",
                "created_at": current_time.isoformat(),
                "profit": 0
            }
            
            # In a real app, save to database
            st.success(f"✅ Aposta registrada!")
            st.json(new_bet)
    
    # TAB 2 - APOSTAS ATIVAS
    with tab2:
        st.subheader("📋 Apostas Pendentes")
        
        if pending:
            for bet in pending:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                    
                    with col1:
                        st.write(f"**{bet.get('match')}**")
                        st.caption(f"🎯 {bet.get('selection')} @ {bet.get('odds')}")
                    with col2:
                        st.write(f"R$ {bet.get('stake', 0):.2f}")
                    with col3:
                        st.write(f"→ R$ {bet.get('potential', 0):.2f}")
                    with col4:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅", key=f"win_{bet.get('id')}"):
                                st.success("Marcada como GANHA")
                        with col_b:
                            if st.button("❌", key=f"lose_{bet.get('id')}"):
                                st.error("Marcada como PERDIDA")
                    
                    st.markdown("---")
        else:
            st.info("Nenhuma aposta pendente")
    
    # TAB 3 - HISTÓRICO
    with tab3:
        st.subheader("📊 Histórico de Apostas")
        
        if all_bets:
            # Convert to simple table
            import pandas as pd
            df_data = []
            for bet in all_bets:
                df_data.append({
                    "Partida": bet.get("match", "N/A"),
                    "Seleção": bet.get("selection", "N/A"),
                    "Odd": bet.get("odds", 0),
                    "Stake": f"R$ {bet.get('stake', 0):.2f}",
                    "Status": bet.get("status", "pending"),
                    "P/L": f"R$ {bet.get('profit', 0):.2f}"
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhuma aposta registrada ainda")
    
    # TAB 4 - CALCULADORA
    with tab4:
        st.subheader("🧮 Calculadora de Value & Kelly")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Value Bet Calculator")
            
            calc_odds = st.number_input("Odd disponível", min_value=1.01, value=2.00, step=0.01, key="calc_odd")
            calc_prob = st.slider("Sua probabilidade (%)", 1, 99, 50, key="calc_prob")
            
            implied = 100 / calc_odds
            value = calc_prob - implied
            ev = (calc_prob/100 * (calc_odds - 1)) - ((100 - calc_prob)/100)
            
            st.markdown("---")
            
            st.metric("📈 Prob. Implícita", f"{implied:.1f}%")
            
            if value > 0:
                st.success(f"✅ VALUE: **+{value:.1f}%**")
                st.success(f"📈 EV: **+{ev*100:.1f}%**")
            else:
                st.error(f"❌ No Value: **{value:.1f}%**")
        
        with col2:
            st.markdown("##### 🎯 Kelly Criterion")
            
            if value > 0:
                kelly_full = (calc_prob/100 * calc_odds - 1) / (calc_odds - 1) * 100
                kelly_half = kelly_full / 2
                kelly_quarter = kelly_full / 4
                
                st.metric("Full Kelly", f"{kelly_full:.1f}%")
                st.metric("Half Kelly (Recomendado)", f"{kelly_half:.1f}%")
                st.metric("Quarter Kelly (Conservador)", f"{kelly_quarter:.1f}%")
                
                st.markdown("---")
                st.caption(f"Para banca de R$ {bankroll:.2f}:")
                st.write(f"• Full: R$ {bankroll * kelly_full/100:.2f}")
                st.write(f"• Half: R$ {bankroll * kelly_half/100:.2f}")
                st.write(f"• Quarter: R$ {bankroll * kelly_quarter/100:.2f}")
            else:
                st.warning("⚠️ Não aposte - sem value")


def render_match_hub():
    """Render Match Hub - Live tracking and match previews."""
    st.title("🎯 Match Hub")
    st.subheader("DreamLeague Season 27 - Live Tracking")
    
    # Import analytics
    try:
        from src.analytics import (
            generate_match_preview, get_dreamleague_teams_analysis,
            get_dreamleague_schedule, calculate_team_form, get_team_hero_pool
        )
        from src.hero_mapper import get_hero_name, get_hero_image_url
        ANALYTICS_AVAILABLE = True
    except ImportError as e:
        st.warning(f"Analytics module not available: {e}")
        ANALYTICS_AVAILABLE = False
    
    # Live clock with auto-refresh info
    import pytz
    sp_tz = pytz.timezone('America/Sao_Paulo')
    current_time = datetime.now(sp_tz)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### ⏰ {current_time.strftime('%H:%M:%S')} BRT")
    with col2:
        st.markdown(f"📅 **{current_time.strftime('%d/%m/%Y')}**")
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📺 Live Now", "📅 Schedule", "🔍 Match Preview", "📊 Team Rankings"])
    
    with tab1:
        render_live_matches()
    
    with tab2:
        if ANALYTICS_AVAILABLE:
            render_schedule()
        else:
            st.info("Schedule not available")
    
    with tab3:
        if ANALYTICS_AVAILABLE:
            render_match_preview_tab()
        else:
            st.info("Match preview not available")
    
    with tab4:
        if ANALYTICS_AVAILABLE:
            render_team_rankings()
        else:
            st.info("Team rankings not available")


def render_live_matches():
    """Render live matches section."""
    st.subheader("📺 Live Matches")
    
    try:
        from src.steam_api import get_all_live_pro_matches, get_dreamleague_live
        from src.hero_mapper import get_hero_name
        
        # Check for live DreamLeague matches first
        dl_live = get_dreamleague_live()
        
        if dl_live:
            st.success(f"🔴 **{len(dl_live)} DreamLeague match(es) LIVE!**")
            
            for game in dl_live:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                    
                    with col1:
                        st.markdown(f"**{game['radiant_team']['name']}**")
                        st.caption(f"Series: {game['radiant_team']['score']}")
                    
                    with col2:
                        st.metric("Kills", game.get('radiant_score', 0))
                    
                    with col3:
                        st.markdown(f"### {game.get('game_time_formatted', '0:00')}")
                        st.caption("vs")
                    
                    with col4:
                        st.metric("Kills", game.get('dire_score', 0))
                    
                    with col5:
                        st.markdown(f"**{game['dire_team']['name']}**")
                        st.caption(f"Series: {game['dire_team']['score']}")
                    
                    # Gold advantage
                    gold_adv = game.get('radiant_gold_adv', 0)
                    if gold_adv > 0:
                        st.progress(min(0.5 + gold_adv / 20000, 1.0), text=f"Radiant +{gold_adv:,}g")
                    else:
                        st.progress(max(0.5 + gold_adv / 20000, 0.0), text=f"Dire +{abs(gold_adv):,}g")
                    
                    # Draft
                    with st.expander("📋 Draft"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Radiant Picks:**")
                            picks = [get_hero_name(h) for h in game.get('radiant_picks', [])]
                            st.write(", ".join(picks) if picks else "Draft in progress...")
                        with col2:
                            st.write("**Dire Picks:**")
                            picks = [get_hero_name(h) for h in game.get('dire_picks', [])]
                            st.write(", ".join(picks) if picks else "Draft in progress...")
                    
                    st.markdown("---")
        else:
            st.info("🔵 No live DreamLeague matches at the moment")
            
            # Check all pro matches
            all_live = get_all_live_pro_matches()
            if all_live:
                st.caption(f"Other live pro matches: {len(all_live)}")
                for game in all_live[:3]:
                    st.write(f"• {game['radiant_team']['name']} vs {game['dire_team']['name']} - {game.get('game_time_formatted', '0:00')}")
            else:
                st.caption("No live pro matches right now")
    
    except ImportError:
        st.warning("Steam API module not available")
        st.info("Install with: pip install requests")
    except Exception as e:
        st.error(f"Error fetching live matches: {e}")


def render_schedule():
    """Render match schedule."""
    st.subheader("📅 DreamLeague S27 Schedule")
    
    from src.analytics import get_dreamleague_schedule
    
    schedule = get_dreamleague_schedule()
    
    if not schedule:
        st.info("No scheduled matches found")
        return
    
    # Group by date
    from collections import defaultdict
    by_date = defaultdict(list)
    for match in schedule:
        by_date[match.get("date", "TBD")].append(match)
    
    for date, matches in sorted(by_date.items()):
        st.markdown(f"### 📅 {date}")
        
        for match in matches:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
                
                with col1:
                    st.write(f"🕐 **{match.get('time_brt', 'TBD')}**")
                    st.caption(f"{match.get('time_cet', '')} CET")
                
                with col2:
                    st.write(f"**{match.get('team_a', 'TBD')}**")
                
                with col3:
                    st.write("**vs**")
                    st.caption(match.get('format', 'Bo3'))
                
                with col4:
                    st.write(f"**{match.get('team_b', 'TBD')}**")
                
                with col5:
                    pred = match.get('prediction')
                    if pred and pred.get('winner'):
                        conf = pred.get('confidence', 50)
                        color = "🟢" if conf >= 60 else "🟡"
                        st.caption(f"{color} {pred['winner'][:10]}")
                        st.caption(f"{conf:.0f}%")
                
                st.markdown("---")


def render_match_preview_tab():
    """Render match preview generator."""
    st.subheader("🔍 Match Preview Generator")
    
    from src.analytics import generate_match_preview, get_team_hero_pool
    from src.hero_mapper import get_hero_name
    
    dl = _load_dreamleague()
    teams = [t.get("name") for t in dl.get("teams", [])]
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        team_a = st.selectbox("Team A", teams, key="preview_team_a")
    with col2:
        team_b = st.selectbox("Team B", [t for t in teams if t != team_a], key="preview_team_b")
    with col3:
        match_format = st.selectbox("Format", ["Bo1", "Bo3", "Bo5"], index=1)
    
    if st.button("🔍 Generate Preview", type="primary"):
        with st.spinner("Analyzing..."):
            preview = generate_match_preview(team_a, team_b, match_format)
        
        if "error" in preview:
            st.error(preview["error"])
            return
        
        # Prediction header
        pred = preview.get("prediction", {})
        winner = pred.get("winner", "Unknown")
        confidence = pred.get("confidence", 50)
        
        if confidence >= 65:
            st.success(f"### 🎯 Predicted Winner: **{winner}** ({confidence:.0f}% confidence)")
        elif confidence >= 55:
            st.info(f"### 🎯 Predicted Winner: **{winner}** ({confidence:.0f}% confidence)")
        else:
            st.warning(f"### 🎯 Close Match - Slight edge to **{winner}** ({confidence:.0f}%)")
        
        # Key factors
        st.markdown("### 📋 Key Factors")
        for factor in preview.get("key_factors", []):
            st.write(f"• {factor}")
        
        # Team comparison
        st.markdown("### 📊 Team Comparison")
        col1, col2 = st.columns(2)
        
        comp = preview.get("team_comparison", {})
        
        with col1:
            ta = comp.get("team_a", {})
            st.markdown(f"#### {ta.get('name', team_a)}")
            st.metric("Rating", f"{ta.get('rating', 0):.0f}")
            form = ta.get("form", {})
            st.write(f"Form: {form.get('form_tier', '?')}")
            st.write(f"Recent WR: {form.get('recent_winrate', 0)}%")
            st.write(f"Top Heroes: {', '.join(ta.get('top_heroes', [])[:3])}")
        
        with col2:
            tb = comp.get("team_b", {})
            st.markdown(f"#### {tb.get('name', team_b)}")
            st.metric("Rating", f"{tb.get('rating', 0):.0f}")
            form = tb.get("form", {})
            st.write(f"Form: {form.get('form_tier', '?')}")
            st.write(f"Recent WR: {form.get('recent_winrate', 0)}%")
            st.write(f"Top Heroes: {', '.join(tb.get('top_heroes', [])[:3])}")
        
        # Contested heroes
        contested = preview.get("contested_heroes", [])
        if contested:
            st.markdown("### ⚔️ Contested Heroes")
            for ch in contested:
                adv = ch.get("advantage_team", ch.get("advantage", "?"))
                st.write(f"• **{ch.get('hero', '?')}** - Advantage: {adv} (+{ch.get('winrate_diff', 0):.0f}% WR)")
        
        # Betting recommendation
        betting = preview.get("betting_analysis", {})
        st.markdown("### 💰 Betting Analysis")
        st.info(f"**{betting.get('recommendation', 'No recommendation')}**")


def render_team_rankings():
    """Render team rankings with drill-down."""
    st.subheader("📊 DreamLeague S27 - Team Rankings")
    
    from src.analytics import get_dreamleague_teams_analysis
    from src.hero_mapper import get_hero_name
    
    teams = get_dreamleague_teams_analysis()
    
    if not teams:
        st.info("No team data available")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Teams", len(teams))
    with col2:
        avg_rating = sum(t.get("rating", 0) for t in teams) / len(teams) if teams else 0
        st.metric("Avg Rating", f"{avg_rating:.0f}")
    with col3:
        hot_teams = len([t for t in teams if "Hot" in t.get("form", {}).get("form_tier", "")])
        st.metric("Hot Form", hot_teams)
    
    st.markdown("---")
    
    # Team list with drill-down
    for i, team in enumerate(teams):
        tier_emoji = {"S": "🟣", "A": "🔵", "B": "🟢", "C": "⚪"}.get(team.get("tier", "C"), "⚪")
        form = team.get("form", {})
        
        with st.expander(f"{i+1}. {tier_emoji} **{team.get('name')}** - ⭐ {team.get('rating', 0):.0f} | {form.get('form_tier', '?')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Rating", f"{team.get('rating', 0):.0f}")
                st.write(f"🌍 Region: {team.get('region', 'N/A')}")
            
            with col2:
                st.metric("Recent WR", f"{team.get('recent_winrate', 0):.0f}%")
                st.write(f"📈 Form: {form.get('form_tier', 'Unknown')}")
            
            with col3:
                st.write("🦸 **Top Heroes:**")
                for hero_id in team.get("top_heroes", [])[:3]:
                    st.write(f"• {get_hero_name(hero_id)}")
            
            # Click to see more details
            if st.button(f"📊 Full Analysis - {team.get('name')}", key=f"team_detail_{i}"):
                st.session_state["selected_team"] = team.get("name")
                st.info(f"Selected: {team.get('name')} - Use Match Preview tab for detailed H2H analysis")


def render_analytics_2025():
    """Render 2025 Analytics Dashboard."""
    st.title("📊 Analytics 2025")
    st.subheader("Análise Estatística de Partidas Pro 2025")
    
    # Try Supabase first, fallback to local JSON
    supabase_data = None
    if USE_DATABASE:
        try:
            from database import get_supabase_client
            client = get_supabase_client()
            if client:
                # Get counts from Supabase
                matches_count = client.table("matches_2025").select("match_id", count="exact").execute()
                picks_count = client.table("picks_bans_2025").select("id", count="exact").execute()
                objectives_count = client.table("objectives_2025").select("id", count="exact").execute()
                teamfights_count = client.table("teamfights_2025").select("id", count="exact").execute()
                
                supabase_data = {
                    "matches": matches_count.count or 0,
                    "picks_bans": picks_count.count or 0,
                    "objectives": objectives_count.count or 0,
                    "teamfights": teamfights_count.count or 0
                }
        except Exception as e:
            st.sidebar.warning(f"Supabase: {e}")
    
    # Fallback to local JSON
    master_path = Path(__file__).parent / "Database" / "2025" / "2025_master.json"
    master_data = load_json(master_path)
    
    if not supabase_data and not master_data:
        st.warning("⚠️ Dados de 2025 não encontrados.")
        
        st.markdown("""
        ### 🔧 Configure os Secrets no Streamlit Cloud:
        
        1. Acesse **Settings** → **Secrets** no painel do Streamlit Cloud
        2. Adicione:
        ```toml
        SUPABASE_URL = "https://gzwkkblksahumnnqlywn.supabase.co"
        SUPABASE_KEY = "sua_anon_key_aqui"
        ```
        3. Salve e aguarde o app reiniciar
        
        **Ou localmente:**
        ```bash
        python scripts/migrate_2025_data.py --all
        ```
        """)
        return
    
    # Summary metrics - prefer Supabase data
    if supabase_data:
        totals = supabase_data
        st.success("🔗 Conectado ao Supabase")
    else:
        totals = master_data.get("totals", {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🎮 Partidas", f"{totals.get('matches', 0):,}")
    with col2:
        st.metric("👥 Players Records", f"{totals.get('players_records', 0):,}")
    with col3:
        st.metric("🎯 Picks/Bans", f"{totals.get('picks_bans', 0):,}")
    with col4:
        st.metric("🏆 Objetivos", f"{totals.get('objectives', 0):,}")
    with col5:
        st.metric("⚔️ Teamfights", f"{totals.get('teamfights', 0):,}")
    
    st.markdown("---")
    
    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Por Mês", "🦸 Heróis Meta", "👥 Times", "📈 Tendências"])
    
    with tab1:
        st.subheader("📅 Estatísticas por Mês")
        
        months_data = master_data.get("months", {})
        
        import pandas as pd
        
        monthly_stats = []
        for month, data in months_data.items():
            summary = data.get("summary", {})
            monthly_stats.append({
                "Mês": month,
                "Partidas": summary.get("total_matches", 0),
                "Players": summary.get("total_player_records", 0),
                "Picks/Bans": summary.get("total_picks_bans", 0),
                "Objetivos": summary.get("total_objectives", 0),
                "Teamfights": summary.get("total_teamfights", 0),
                "Chat": summary.get("total_chat_messages", 0)
            })
        
        if monthly_stats:
            df = pd.DataFrame(monthly_stats)
            st.dataframe(df, use_container_width=True)
            
            # Chart
            st.bar_chart(df.set_index("Mês")["Partidas"])
    
    with tab2:
        st.subheader("🦸 Hero Meta Analysis")
        
        # Load from Supabase
        if USE_DATABASE and supabase_data:
            try:
                from database import get_supabase_client
                client = get_supabase_client()
                if client:
                    # Get hero pick/ban stats directly
                    result = client.table("picks_bans_2025")\
                        .select("hero_id, is_pick")\
                        .limit(100000)\
                        .execute()
                    
                    if result.data:
                        import pandas as pd
                        df = pd.DataFrame(result.data)
                        
                        if "hero_id" in df.columns and len(df) > 0:
                            picks = df[df["is_pick"] == True].groupby("hero_id").size()
                            bans = df[df["is_pick"] == False].groupby("hero_id").size()
                            
                            hero_stats = pd.DataFrame({
                                "Picks": picks,
                                "Bans": bans
                            }).fillna(0).astype(int)
                            
                            hero_stats["Total"] = hero_stats["Picks"] + hero_stats["Bans"]
                            hero_stats["Pick Rate %"] = (hero_stats["Picks"] / hero_stats["Total"] * 100).round(1)
                            hero_stats = hero_stats.sort_values("Total", ascending=False).head(30)
                            
                            st.dataframe(hero_stats, use_container_width=True)
                            
                            # Top picks chart
                            st.bar_chart(hero_stats["Picks"].head(15))
                        else:
                            st.info("Nenhum dado de heróis encontrado")
                    else:
                        st.info("Tabela picks_bans_2025 vazia")
            except Exception as e:
                st.warning(f"Erro ao carregar heróis: {e}")
        else:
            st.info("Conecte ao Supabase para ver análise de heróis")
    
    with tab3:
        st.subheader("👥 Team Performance")
        
        # Load from Supabase - get teams from matches
        if USE_DATABASE and supabase_data:
            try:
                from database import get_supabase_client
                client = get_supabase_client()
                if client:
                    # Get radiant/dire team stats
                    result = client.table("matches_2025")\
                        .select("radiant_team_id, dire_team_id, radiant_win")\
                        .not_.is_("radiant_team_id", "null")\
                        .limit(10000)\
                        .execute()
                    
                    if result.data:
                        import pandas as pd
                        df = pd.DataFrame(result.data)
                        
                        # Count matches per team
                        radiant_counts = df["radiant_team_id"].value_counts()
                        dire_counts = df["dire_team_id"].value_counts()
                        
                        # Combine
                        all_teams = set(radiant_counts.index) | set(dire_counts.index)
                        team_stats = []
                        for team_id in all_teams:
                            rad = radiant_counts.get(team_id, 0)
                            dire = dire_counts.get(team_id, 0)
                            # Calculate wins
                            rad_wins = len(df[(df["radiant_team_id"] == team_id) & (df["radiant_win"] == True)])
                            dire_wins = len(df[(df["dire_team_id"] == team_id) & (df["radiant_win"] == False)])
                            total_matches = rad + dire
                            total_wins = rad_wins + dire_wins
                            winrate = (total_wins / total_matches * 100) if total_matches > 0 else 0
                            
                            team_stats.append({
                                "Team ID": team_id,
                                "Matches": total_matches,
                                "Wins": total_wins,
                                "Win Rate %": round(winrate, 1)
                            })
                        
                        team_df = pd.DataFrame(team_stats).sort_values("Matches", ascending=False).head(30)
                        st.dataframe(team_df, use_container_width=True)
                        
                        # Chart
                        st.bar_chart(team_df.set_index("Team ID")["Matches"].head(15))
            except Exception as e:
                st.warning(f"Erro ao carregar times: {e}")
        else:
            st.info("Conecte ao Supabase para ver dados de times")
    
    with tab4:
        st.subheader("📈 Tendências")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Volume de Partidas**")
            months_data = master_data.get("months", {})
            matches_by_month = {
                m: d.get("summary", {}).get("total_matches", 0)
                for m, d in months_data.items()
            }
            
            import pandas as pd
            df = pd.DataFrame([
                {"Mês": k, "Partidas": v}
                for k, v in matches_by_month.items()
            ])
            if not df.empty:
                st.line_chart(df.set_index("Mês"))
        
        with col2:
            st.markdown("**⚔️ Teamfights por Mês**")
            tf_by_month = {
                m: d.get("summary", {}).get("total_teamfights", 0)
                for m, d in months_data.items()
            }
            
            df_tf = pd.DataFrame([
                {"Mês": k, "Teamfights": v}
                for k, v in tf_by_month.items()
            ])
            if not df_tf.empty:
                st.line_chart(df_tf.set_index("Mês"))


if __name__ == "__main__":
    main()
