import json
import random

class GameState:
    def __init__(self):
        self.team1_players = []
        self.team2_players = []
        self.team1_color = "#3498db" 
        self.team2_color = "#e74c3c" 
        self.coalition_party = None
        self.opposition_party = None
        self.ratings = {"coalition": 50, "opposition": 50}
        self.player_weights = {}  
        self.current_round = 1
        self.max_rounds = 4
        self.history = []
        self.events = self._load_data("data/events.json")
        self.laws = self._load_data("data/laws.json")
        self.current_event = None
        self.veto_used = False

    def _load_data(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def set_roles(self, rating1, rating2, team1_names, team2_names):
        self.team1_players = team1_names
        self.team2_players = team2_names
        
        total = rating1 + rating2
        if total == 0: total = 1
        r1 = (rating1 / total) * 100
        r2 = 100 - r1

        if r1 >= r2:
            self.coalition_party = "Team 1"
            self.opposition_party = "Team 2"
            self.ratings["coalition"] = r1
            self.ratings["opposition"] = r2
        else:
            self.coalition_party = "Team 2"
            self.opposition_party = "Team 1"
            self.ratings["coalition"] = r2
            self.ratings["opposition"] = r1
        
        self._update_weights()

    def next_round(self):
        if self.current_round <= self.max_rounds:
            available_events = [e for e in self.events if e["id"] != (self.current_event["id"] if self.current_event else None)]
            self.current_event = random.choice(available_events) if available_events else (self.events[0] if self.events else None)
            self.veto_used = False
            
            swing_report = None
            if random.random() < 0.3:
                swing = random.randint(1, 1) 
                direction = random.choice([1, -1])
                self._change_rating(swing * direction)
                topic = random.choice([
                    "Wirtschaftsnachrichten", "Umfrageergebnisse", "Globale Trends", 
                    "Gesellschaftliche Stimmung", "Medienberichte"
                ])
                msg = f"🗞 {topic}: Die Stimmung hat sich um {swing}% zugunsten der {'Koalition' if direction > 0 else 'Opposition'} verschoben."
                swing_report = {"effects": [msg]}
            
            self.current_round += 0 
            return self.current_event, swing_report
        return None, None

    def _change_rating(self, delta):
        self.ratings["coalition"] = max(0, min(100, self.ratings["coalition"] + delta))
        self.ratings["opposition"] = 100 - self.ratings["coalition"]

    def apply_law(self, law_id):
        law = next((l for l in self.laws if l["id"] == law_id), None)
        if not law: return None
        
        report = {"law_title": law["title"], "effects": []}
        
        impact = law.get("impact", 0)
        
        if random.random() < 0.05:
            impact -= 4
            report["effects"].append("🔍 Die Opposition hat eine Schwachstelle gefunden: -4% zum Einfluss!")

        self._change_rating(impact)
        report["effects"].append(f"Koalitionsrating: {'+' if impact >=0 else ''}{impact}%")

        rand = random.random()
        pos_chance = law.get("intl_pos", 0) * 0.8
        neg_chance = law.get("intl_neg", 0)
        
        if rand < pos_chance:
            bonus = random.randint(1, 4)
            self._change_rating(bonus)
            report["effects"].append(f"🌍 Positive internationale Reaktion: +{bonus}%")
        elif rand > (1 - neg_chance):
            penalty = random.randint(2, 4)
            self._change_rating(-penalty)
            report["effects"].append(f"🌍 Negative internationale Reaktion: -{penalty}%")
        
        if random.random() < law.get("scandal_chance", 0):
            scandal_impact = random.randint(5, 8)
            self._change_rating(-scandal_impact)
            report["effects"].append(f"⚠️ Regierungsskandal: -{scandal_impact}%")

        self._update_weights()
        return report

    def handle_no_laws(self):
        report = {"effects": []}
        c, o = self.ratings["coalition"], self.ratings["opposition"]
        
        # Popularity penalty for inactivity
        if c > o or random.random() < 0.5:
            self._change_rating(-5)
            report["effects"].append("❌ Keine Gesetze verabschiedet: -5% (Wählerunzufriedenheit)")
        
        if random.random() < 0.05:
            scandal_impact = random.randint(5, 8)
            self._change_rating(-scandal_impact)
            report["effects"].append(f"⚠️ Zufälliger Korruptionsskandal: -{scandal_impact}%")
            
        self._update_weights()
        return report

    def _update_weights(self):
        c_norm = self.ratings["coalition"]
        o_norm = self.ratings["opposition"]
        
        if self.coalition_party == "Team 1":
            c_players, o_players = self.team1_players, self.team2_players
        else:
            c_players, o_players = self.team2_players, self.team1_players
            
        for p in c_players: self.player_weights[p] = round(c_norm / len(c_players), 1) if c_players else 0
        for p in o_players: self.player_weights[p] = round(o_norm / len(o_players), 1) if o_players else 0
