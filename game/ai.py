import openai
import os
import json
import random
from dotenv import load_dotenv
import streamlit as st

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path, override=True)

class AIConsultant:
    def __init__(self, api_key=None):
        self.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def evaluate_campaigns(self, text1, text2):
        if not self.api_key or self.api_key == "None":
            r1 = random.randint(40, 60)
            return {
                "status": "success",
                "party1": {"rating": r1, "feedback": "Simulation: Team 1."},
                "party2": {"rating": 100 - r1, "feedback": "Simulation: Team 2."}
            }

        prompt = f"""
            Du agierst als ein Simulator für politische Wahlen. Deine Aufgabe ist es, echte Wahlen in Deutschland zu simulieren.

Es gibt zwei Parteien mit folgenden Programmen:

Partei A:
{text1}
Partei B:
{text2}

Aufgaben:

1. Teile das Wählersegment in 5 Gruppen auf:
   - Jugend
   - Mittelstand
   - Rentner
   - Unternehmer
   - Sozial schwache Gruppen

2. Für jede Gruppe:
   - Beschreibe kurz, was für sie am wichtigsten ist.
   - Bewerte die Attraktivität jeder Partei auf einer Skala von 0 bis 10.
   - Jede Gruppe hat eine eigene Gewichtung basierend auf ihrer Größe in Deutschland (z.B. gibt es viele Rentner, deren Einfluss ist also groß).

3. Füge einen externen Faktor hinzu (Wirtschaftskrise, lauter Skandal, starke TV-Debatten, Migrationswelle oder Umweltkatastrophe) und erkläre dessen Einfluss (+/- 3%).

4. Basierend auf diesen Faktoren modelliere die endgültige Verteilung von 100% der Stimmen.

5. Sonderregel für Unklarheit:
   - Wenn ein Programm unklar oder unsinnig ist, erhält diese Partei nur 26% bis 29% der Stimmen.
   - Wenn beide Programme unklar sind, wähle das realistischere von beiden und gib ihm 51% bis 62%.

WICHTIG:
- Versuche nicht, das Ergebnis künstlich auszubalancieren.
- Jedes Verhältnis von 20/80 bis 80/20 ist zulässig.
- Wenn eine Partei wesentlich stärker ist, muss sich das in den Zahlen widerspiegeln.
- Begründe die endgültigen Prozentsätze.

Gültigkeitsprüfung:
Wenn mindestens eine Kampagne:
- Aus zufälligen Zeichen besteht,
- Nichts mit Wahlen zu tun hat,
dann setze:
"status": "invalid"
und erkläre das Problem auf Deutsch im Feld "error_msg".

Im Falle von "invalid":
- Verteile keine Stimmen.
- Erfinde keine Bewertungen.

Gib die Antwort STRENG im JSON-Format ohne zusätzlichen Text zurück:

            {{
             "status": "success" oder "invalid",
             "error_msg": "Problembeschreibung auf Deutsch oder leerer String bei success",
             "party1": {{ "rating": integer (20-80), "feedback": "Kommentar für Team 1 (max. 2 Sätze)" }}, 
             "party2": {{ "rating": integer (20-80), "feedback": "Kommentar für Team 2 (max. 2 Sätze)" }}
            }}
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini", 
                messages=[{"role": "system", "content": "Du bist ein unparteiischer politischer Experte."},
                          {"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            print(result)
            if result.get("status") == "invalid":
                return result

            p1_r = result["party1"]["rating"]
            p2_r = result["party2"]["rating"]
            
            p1_r = max(20, min(80, p1_r))
            p2_r = 100 - p1_r 
            
            if p2_r < 20:
                p2_r = 20
                p1_r = 80
            elif p2_r > 80:
                p2_r = 80
                p1_r = 20
            
            result["party1"]["rating"] = p1_r
            result["party2"]["rating"] = p2_r
            result["status"] = "success"
            
            return result
        except Exception as e:
            r1 = random.randint(45, 55)
            print(r1)
            return {
                "status": "error",
                "error_msg": str(e),
                "party1": {"rating": r1, "feedback": f"Fehler KI: {str(e)}"},
                "party2": {"rating": 100 - r1, "feedback": "Standardverteilung."}
            }

