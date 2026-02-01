# Cloud9 Scouting Agent - Automated Scouting Report Generator

**Cloud9 x JetBrains Hackathon - Category 2 Submission**

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Features

- **Mock Data Mode**: Simulates 5 recent matches for testing (ready for GRID API integration)
- **Top Bans Analysis**: Identifies top 3 champions to ban based on win rate and pick rate
- **One-Trick Detection**: Highlights players who favor specific champions (>60% play rate)
- **Aggression Score**: Calculates first blood percentage
- **K/D Trend Analysis**: Visual chart of team performance
- **Export Reports**: Download scouting reports as .txt files

## 🔧 GRID API Integration

When you receive your GRID API key, replace the mock data function:

1. Open `app.py`
2. Find the `get_mock_team_data()` function (line ~20)
3. Replace with actual API call:

```python
import requests

def get_team_data(team_name, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        f"https://api.grid.gg/teams/{team_name}/matches",
        headers=headers
    )
    return response.json()
```

4. Update line ~250 in `main()` function to use real data

## 🎮 Tech Stack

- **Python 3.8+**
- **Streamlit** - Fast UI framework
- **Pandas** - Data manipulation

## 📊 Analytics Functions

- `get_top_bans()` - Champion ban priority
- `detect_one_tricks()` - Player champion preferences
- `team_aggression_score()` - First blood statistics
- `calculate_kd_ratio_per_game()` - Performance metrics

## 🎨 UI Features

- Dark esports-themed design
- Real-time team selection
- Interactive metrics and charts
- Downloadable reports

---

**Cloud9 x JetBrains Hackathon**
