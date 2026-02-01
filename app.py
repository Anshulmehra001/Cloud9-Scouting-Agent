"""
Automated Scouting Report Generator for League of Legends
Stack: Python + Streamlit + Pandas
"""

import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from collections import Counter

# ============================================================================
# 1. MOCK DATA GENERATOR
# ============================================================================
# TODO: Replace this function with actual GRID API call when API key is ready
# API Endpoint: https://api.grid.gg/... (add your endpoint here)
# Headers: {"Authorization": "Bearer YOUR_API_KEY"}

def get_mock_team_data(team_name):
    """
    Simulates GRID API response for 5 recent matches of a team.
    
    Args:
        team_name (str): Name of the team to fetch data for
    
    Returns:
        list: List of match dictionaries with player stats
    """
    
    # Mock player pools for different teams
    team_rosters = {
        "Team Liquid": {
            "Top": "Impact",
            "Jungle": "Umti",
            "Mid": "APA",
            "ADC": "Yeon",
            "Support": "CoreJJ"
        },
        "Cloud9": {
            "Top": "Thanatos",
            "Jungle": "Blaber",
            "Mid": "Jojopyun",
            "ADC": "Berserker",
            "Support": "Vulcan"
        },
        "FlyQuest": {
            "Top": "Bwipo",
            "Jungle": "Inspired",
            "Mid": "Quad",
            "ADC": "Massu",
            "Support": "Busio"
        }
    }
    
    # Champion pools (realistic LoL champions)
    champion_pool = {
        "Top": ["Aatrox", "Gnar", "K'Sante", "Renekton", "Jax", "Ornn"],
        "Jungle": ["Lee Sin", "Vi", "Jarvan IV", "Graves", "Elise", "Viego"],
        "Mid": ["Azir", "Orianna", "Syndra", "Ahri", "Viktor", "Sylas"],
        "ADC": ["Jinx", "Kai'Sa", "Aphelios", "Jhin", "Ezreal", "Caitlyn"],
        "Support": ["Thresh", "Nautilus", "Leona", "Lulu", "Renata Glasc", "Rell"]
    }
    
    roster = team_rosters.get(team_name, team_rosters["Team Liquid"])
    matches = []
    
    # Generate 5 matches
    for i in range(5):
        match_date = datetime.now() - timedelta(days=i*3)
        match = {
            "match_id": f"MATCH_{random.randint(10000, 99999)}",
            "date": match_date.strftime("%Y-%m-%d"),
            "outcome": random.choice(["Win", "Win", "Win", "Loss", "Loss"]),  # Slight win bias
            "first_blood": random.choice([True, False]),
            "players": []
        }
        
        # Generate player stats for each role
        for role in ["Top", "Jungle", "Mid", "ADC", "Support"]:
            player_name = roster[role]
            
            # Some players have champion preferences (one-tricks)
            if random.random() > 0.7:  # 30% chance of one-trick behavior
                champion = random.choice(champion_pool[role][:2])  # Prefer first 2 champs
            else:
                champion = random.choice(champion_pool[role])
            
            # Generate realistic KDA
            kills = random.randint(0, 12)
            deaths = random.randint(0, 6)
            assists = random.randint(2, 15)
            
            match["players"].append({
                "role": role,
                "player_name": player_name,
                "champion": champion,
                "kills": kills,
                "deaths": deaths,
                "assists": assists
            })
        
        matches.append(match)
    
    return matches


# ============================================================================
# 2. ANALYTICS ENGINE
# ============================================================================

def get_top_bans(data):
    """
    Identify top 3 champions with highest win rate or pick rate.
    
    Args:
        data (list): List of match dictionaries
    
    Returns:
        list: Top 3 champions to ban with their stats
    """
    champion_stats = {}
    
    for match in data:
        outcome = match["outcome"]
        for player in match["players"]:
            champion = player["champion"]
            
            if champion not in champion_stats:
                champion_stats[champion] = {"wins": 0, "picks": 0, "total_games": 0}
            
            champion_stats[champion]["picks"] += 1
            champion_stats[champion]["total_games"] += 1
            
            if outcome == "Win":
                champion_stats[champion]["wins"] += 1
    
    # Calculate win rates and sort
    ban_priority = []
    for champ, stats in champion_stats.items():
        win_rate = (stats["wins"] / stats["total_games"]) * 100 if stats["total_games"] > 0 else 0
        pick_rate = (stats["picks"] / len(data)) * 100
        
        # Priority score: win rate + pick rate (champions picked often and winning)
        priority_score = win_rate + (pick_rate * 0.5)
        
        ban_priority.append({
            "champion": champ,
            "win_rate": win_rate,
            "pick_rate": pick_rate,
            "priority_score": priority_score
        })
    
    # Sort by priority score and return top 3
    ban_priority.sort(key=lambda x: x["priority_score"], reverse=True)
    return ban_priority[:3]


def detect_one_tricks(data):
    """
    Identify players who play the same champion in >60% of matches.
    
    Args:
        data (list): List of match dictionaries
    
    Returns:
        list: Players with their signature champions
    """
    player_champions = {}
    
    for match in data:
        for player in match["players"]:
            player_name = player["player_name"]
            champion = player["champion"]
            
            if player_name not in player_champions:
                player_champions[player_name] = []
            
            player_champions[player_name].append(champion)
    
    one_tricks = []
    
    for player, champions in player_champions.items():
        champion_counts = Counter(champions)
        most_common = champion_counts.most_common(1)[0]
        champion_name, count = most_common
        
        play_rate = (count / len(champions)) * 100
        
        if play_rate > 60:
            one_tricks.append({
                "player": player,
                "signature_champion": champion_name,
                "play_rate": play_rate,
                "games_played": count
            })
    
    return one_tricks


def team_aggression_score(data):
    """
    Calculate % of games where team got First Blood.
    
    Args:
        data (list): List of match dictionaries
    
    Returns:
        float: Percentage of games with first blood
    """
    first_blood_count = sum(1 for match in data if match["first_blood"])
    total_games = len(data)
    
    return (first_blood_count / total_games) * 100 if total_games > 0 else 0


def calculate_kd_ratio_per_game(data):
    """
    Calculate team K/D ratio for each game.
    
    Args:
        data (list): List of match dictionaries
    
    Returns:
        list: K/D ratios per game
    """
    kd_ratios = []
    
    for match in data:
        total_kills = sum(p["kills"] for p in match["players"])
        total_deaths = sum(p["deaths"] for p in match["players"])
        
        kd_ratio = total_kills / total_deaths if total_deaths > 0 else total_kills
        kd_ratios.append({
            "match_id": match["match_id"],
            "date": match["date"],
            "kd_ratio": round(kd_ratio, 2)
        })
    
    return kd_ratios


def calculate_win_probability(data):
    """
    Calculate predicted win probability based on recent performance.
    
    Args:
        data (list): List of match dictionaries
    
    Returns:
        float: Win probability percentage
    """
    wins = sum(1 for match in data if match["outcome"] == "Win")
    total_games = len(data)
    
    return (wins / total_games) * 100 if total_games > 0 else 0


# ============================================================================
# 3. STREAMLIT FRONTEND
# ============================================================================

def main():
    # Dark mode configuration
    st.set_page_config(
        page_title="Cloud9 Scouting Agent",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for dark esports aesthetic
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
        }
        .stMetric {
            background-color: #1e2130;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #00d4ff;
        }
        h1 {
            color: #00d4ff;
            font-family: 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        h2, h3 {
            color: #ffffff;
            font-family: 'Arial', sans-serif;
        }
        .ban-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("# 🎮 CLOUD9 SCOUTING AGENT // ONE-SHEET SCOUT")
    st.markdown("---")
    
    # Team selection
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_team = st.selectbox(
            "🎯 Select Enemy Team:",
            ["Team Liquid", "Cloud9", "FlyQuest"]
        )
    
    # Fetch data (mock for now)
    # TODO: Replace with actual API call
    # response = requests.get(f"https://api.grid.gg/teams/{selected_team}/matches", headers={"Authorization": f"Bearer {API_KEY}"})
    # team_data = response.json()
    team_data = get_mock_team_data(selected_team)
    
    # Calculate analytics
    win_prob = calculate_win_probability(team_data)
    aggression = team_aggression_score(team_data)
    top_bans = get_top_bans(team_data)
    one_tricks = detect_one_tricks(team_data)
    kd_ratios = calculate_kd_ratio_per_game(team_data)
    
    # Header Metrics
    st.markdown("### 📊 KEY INTEL")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="🏆 Predicted Win Probability",
            value=f"{win_prob:.1f}%",
            delta=f"{win_prob - 50:.1f}% vs average"
        )
    
    with metric_col2:
        st.metric(
            label="⚔️ Aggression Score",
            value=f"{aggression:.1f}%",
            delta="First Blood Rate"
        )
    
    with metric_col3:
        total_games = len(team_data)
        wins = sum(1 for m in team_data if m["outcome"] == "Win")
        st.metric(
            label="📈 Recent Form",
            value=f"{wins}W - {total_games - wins}L",
            delta=f"Last {total_games} games"
        )
    
    st.markdown("---")
    
    # Row 1: Suggested Bans
    st.markdown("### 🚫 SUGGESTED BANS")
    ban_cols = st.columns(3)
    
    for idx, ban in enumerate(top_bans):
        with ban_cols[idx]:
            st.markdown(f"""
                <div class="ban-card">
                    <h2>#{idx + 1} {ban['champion']}</h2>
                    <p>Win Rate: {ban['win_rate']:.1f}%</p>
                    <p>Pick Rate: {ban['pick_rate']:.1f}%</p>
                    <p>Priority: {ban['priority_score']:.1f}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Row 2: Player Tendencies (One-Tricks)
    st.markdown("### 🎯 PLAYER TENDENCIES // ONE-TRICK DETECTION")
    
    if one_tricks:
        df_one_tricks = pd.DataFrame(one_tricks)
        df_one_tricks = df_one_tricks.rename(columns={
            "player": "Player",
            "signature_champion": "Signature Champion",
            "play_rate": "Play Rate (%)",
            "games_played": "Games on Champion"
        })
        
        st.dataframe(
            df_one_tricks,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No one-trick players detected. Team shows diverse champion pool.")
    
    st.markdown("---")
    
    # Row 3: K/D Ratio Chart
    st.markdown("### 📈 TEAM K/D RATIO TREND")
    
    df_kd = pd.DataFrame(kd_ratios)
    st.bar_chart(df_kd.set_index("date")["kd_ratio"], use_container_width=True)
    
    st.markdown("---")
    
    # Download Report Button
    st.markdown("### 💾 EXPORT REPORT")
    
    report_text = f"""
CLOUD9 SCOUTING REPORT
======================
Target Team: {selected_team}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

KEY METRICS
-----------
Win Probability: {win_prob:.1f}%
Aggression Score: {aggression:.1f}%
Recent Form: {wins}W - {total_games - wins}L

SUGGESTED BANS
--------------
"""
    
    for idx, ban in enumerate(top_bans):
        report_text += f"{idx + 1}. {ban['champion']} (Win Rate: {ban['win_rate']:.1f}%, Pick Rate: {ban['pick_rate']:.1f}%)\n"
    
    report_text += "\nPLAYER TENDENCIES\n-----------------\n"
    
    if one_tricks:
        for ot in one_tricks:
            report_text += f"- {ot['player']}: {ot['signature_champion']} ({ot['play_rate']:.1f}% play rate)\n"
    else:
        report_text += "No one-trick players detected.\n"
    
    report_text += "\nK/D RATIO PER GAME\n------------------\n"
    for kd in kd_ratios:
        report_text += f"{kd['date']}: {kd['kd_ratio']}\n"
    
    st.download_button(
        label="📥 Download Scouting Report (.txt)",
        data=report_text,
        file_name=f"scouting_report_{selected_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <p style='text-align: center; color: #666;'>
        Cloud9 x JetBrains Hackathon | Category 2: Automated Scouting Report Generator
        </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
