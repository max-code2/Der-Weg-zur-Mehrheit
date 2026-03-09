import streamlit as st
import time
from game.state import GameState
from game.ai import AIConsultant
from game.mechanics import GameMechanics
import os

st.set_page_config(page_title="Der Weg zur Mehrheit", layout="wide", page_icon="🏛")

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background-color: #0e1117;
        color: #f0f0f0;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .fade-in {
        animation: fadeIn 0.8s ease-out forwards;
    }

    .float-anim {
        animation: float 3s ease-in-out infinite;
    }

    .stButton>button {
        background: linear-gradient(90deg, #ff8c00 0%, #ff4500 100%) !important;
        color: white !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 69, 0, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 69, 0, 0.5) !important;
        filter: brightness(1.1) !important;
    }

   
    .stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox [data-baseweb="select"] > div:focus {
        border-color: rgba(255, 69, 0, 0.4) !important;
        box-shadow: 0 0 0 2px rgba(255, 69, 0, 0.1) !important;
    }

    .stCheckbox [data-testid="stCheckbox"] > label > div:first-child {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    .stCheckbox:hover [data-testid="stCheckbox"] > label > div:first-child {
        border-color: rgba(255, 69, 0, 0.5) !important;
        background: rgba(255, 69, 0, 0.05) !important;
    }

    [data-testid="stMetricValue"] {
        animation: pulseRating 1.5s ease-out;
    }

    @keyframes pulseRating {
        0% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.3); text-shadow: 0 0 10px rgba(255,255,255,0.5); }
        100% { transform: scale(1); filter: brightness(1); }
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }

    .hero-title {
        font-size: 4.5rem;
        font-weight: 700;
        background: linear-gradient(to bottom, #ffffff, #888888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }

    .hero-subtitle {
        text-align: center;
        color: #ff4500;
        font-size: 1.4rem;
        font-weight: 600;
        letter-spacing: 2px;
        margin-bottom: 3rem;
    }

    .loader {
        border: 4px solid rgba(255, 255, 255, 0.1);
        border-top: 4px solid #ff4500;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .player-tag {
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9em;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if "game" not in st.session_state:
    st.session_state.game = GameState()
if "step" not in st.session_state:
    st.session_state.step = "splash"

inject_custom_css()

def colored_name(name, color):
    return f'<span class="player-tag" style="background-color: {color}33; color: {color}; border: 1px solid {color}55;">{name}</span>'

def start_game():
    st.session_state.step = "start"
    st.rerun()

def start_setup():
    st.session_state.step = "setup"
    st.rerun()

def start_campaign():
    t1_names = [st.session_state[f"t1_p{i}"] for i in range(st.session_state.t1_count) if st.session_state.get(f"t1_p{i}")]
    t2_names = [st.session_state[f"t2_p{i}"] for i in range(st.session_state.t2_count) if st.session_state.get(f"t2_p{i}")]
    
    if len(t1_names) < 2 or len(t2_names) < 2:
        st.error("Jedes Team muss mindestens 2 Spieler haben!")
        return
        
    st.session_state.game.team1_color = st.session_state.t1_color_pick
    st.session_state.game.team2_color = st.session_state.t2_color_pick
    st.session_state.t1_names = t1_names
    st.session_state.t2_names = t2_names
    st.session_state.step = "campaign"
    st.rerun()

def submit_campaign():
    ai = AIConsultant() 
    text1 = st.session_state.player1_campaign
    text2 = st.session_state.player2_campaign
    
    if not text1 or not text2:
        st.error("Bitte fülle beide Wahlkampagnen aus!")
        return

    with st.spinner("ChatGPT bewertet eure Kampagnen..."):
        results = ai.evaluate_campaigns(text1, text2)
    
    if results.get("status") == "invalid":
        st.error(f"🚫 Problem mit dem Kampagnentext: {results.get('error_msg', 'Eine der Kampagnen ist unverständlich')}")
        return
    elif results.get("status") == "error":
        st.warning(f"⚠️ KI-Fehler: {results.get('error_msg')}. Zufällige Ergebnisse wurden verwendet.")
    
    st.session_state.ai_results = results
    st.session_state.game.set_roles(
        results["party1"]["rating"], 
        results["party2"]["rating"], 
        st.session_state.t1_names, 
        st.session_state.t2_names
    )
    st.session_state.step = "roles_display"
    st.rerun()

def next_round_ui():
    event, swing_report = st.session_state.game.next_round()
    if event:
        st.session_state.step = "round"
        st.session_state.round_laws = [l for l in st.session_state.game.laws if l["event_id"] == event["id"]]
        st.session_state.current_votes = {law["id"]: {} for law in st.session_state.round_laws}
        st.session_state.round_reports = [] if not swing_report else [swing_report]
    else:
        st.session_state.step = "end"
    st.rerun()


def render_splash():
    st.markdown('<div style="height: 30vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-top: 2rem;">Lade Der Weg zur Mehrheit...</h2>', unsafe_allow_html=True)
    time.sleep(1.2)
    start_game()

def render_start():
    st.markdown('<div class="fade-in"><div class="float-anim"><div class="hero-title">🏛 DER WEG ZUR MEHRHEIT</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">MACHT • STRATEGIE • WAHL</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center;" class="fade-in">
            <h3>📜 SPIELREGELN</h3>
            <p style="color: #888;">Bilde ein Team, schreibe eine überzeugende Kampagne und verabschiede Gesetze, um die Herzen der Wähler zu gewinnen.</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Mindestens 4 Spieler (2 pro Team).</li>
                <li>Das Spiel dauert 4 Runden.</li>
                <li>Die KI bewertet deine Wahlkampagne.</li>
                <li>Das Gewicht deiner Stimme hängt vom Parteiranking ab.</li>
                <li>Gesetze werden verabschiedet, wenn sie ≥ 50% Unterstützung erhalten.</li>
                <li>Wichtig: Diskutiert die Gesetze gemeinsam für ein vollwertiges Spielerlebnis.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("SPIELEN", use_container_width=True):
                start_setup()

def render_setup():
    st.markdown('<h2 style="text-align: center;" class="fade-in">👥 TEAM-EINSTELLUNGEN</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Team 1")
            st.color_picker("Teamfarbe", "#1E90FF", key="t1_color_pick")
            t1_count = st.number_input("Anzahl der Spieler (T1)", 2, 5, 2, key="t1_count")
            for i in range(t1_count):
                st.text_input(f"Spieler {i+1}", key=f"t1_p{i}", value=f"Spieler A{i+1}")
    with col2:
        with st.container(border=True):
            st.subheader("Team 2")
            st.color_picker("Teamfarbe", "#FF4500", key="t2_color_pick")
            t2_count = st.number_input("Anzahl der Spieler (T2)", 2, 5, 2, key="t2_count")
            for i in range(t2_count):
                st.text_input(f"Spieler {i+1}", key=f"t2_p{i}", value=f"Spieler B{i+1}")
    if st.button("WEITER", use_container_width=True):
        start_campaign()

def render_campaign():
    st.header("📢 Wahlkampagne")
    st.write("Schreibe eine Kampagne für die Wähler in Deutschland. Die KI bestimmt eure Startstimmen.")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Kampagne 1")
            st.text_area("Deine Wahlkampagne...", key="player1_campaign", height=150,
                         placeholder="Beispiel: Wir sichern eine stabile Zukunft durch Digitalisierung und neue Arbeitsplätze...")
    with col2:
        with st.container(border=True):
            st.subheader("Kampagne 2")
            st.text_area("Deine Wahlkampagne...", key="player2_campaign", height=150,
                         placeholder="Beispiel: Unsere Priorität ist soziale Gerechtigkeit und die Unterstützung der Rentner...")
    if st.button("ZUR BEWERTUNG SENDEN", use_container_width=True):
        submit_campaign()

def render_roles_display():
    st.header("📊 Wahlergebnisse")
    game = st.session_state.game
    res = st.session_state.ai_results
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Team 1", f"{res['party1']['rating']}%")
            st.write(f"_{res['party1']['feedback']}_")
    with col2:
        with st.container(border=True):
            st.metric("Team 2", f"{res['party2']['rating']}%")
            st.write(f"_{res['party2']['feedback']}_")
    st.divider()
    st.subheader("🗳 Stimmgewicht der Spieler")
    cols = st.columns(len(game.player_weights))
    for i, (name, weight) in enumerate(game.player_weights.items()):
        is_t1 = name in game.team1_players
        color = game.team1_color if is_t1 else game.team2_color
        with cols[i]:
            st.markdown(f'<div style="text-align: center;" class="fade-in">{colored_name(name, color)}<br><b>{weight:.1f}%</b></div>', unsafe_allow_html=True)
    if st.button("ZUR ERSTEN RUNDE", use_container_width=True):
        next_round_ui()

def render_round():
    game = st.session_state.game
    st.markdown(f'<h2 style="text-align: center;">🛡 Runde {game.current_round}: {game.current_event["title"]}</h2>', unsafe_allow_html=True)
    st.warning(game.current_event['description'])
    st.divider()
    st.subheader("📝 Abstimmung über Gesetze")
    
    for law in st.session_state.round_laws:
        with st.container(border=True):
            st.markdown(f"#### 📜 {law['title']}")
            st.write(law['description'])
            
            all_players = game.team1_players + game.team2_players
            cols = st.columns(len(all_players))
            for i, p_name in enumerate(all_players):
                p_color = game.team1_color if p_name in game.team1_players else game.team2_color
                st.session_state.current_votes[law['id']][p_name] = cols[i].checkbox(
                    p_name, 
                    key=f"vote_{law['id']}_{p_name}_{game.current_round}",
                    help=f"Stimmgewicht: {game.player_weights[p_name]:.1f}%"
                )

    st.divider()
    if st.button("ERGEBNISSE BERECHNEN", use_container_width=True):
        passed_laws = []
        for law in st.session_state.round_laws:
            if GameMechanics.check_law_passed(st.session_state.current_votes[law['id']], game.player_weights):
                passed_laws.append(law)
        st.session_state.passed_this_round = passed_laws
        st.session_state.step = "veto_screen"
        st.rerun()

def render_veto_screen():
    game = st.session_state.game
    st.header("🛡 Veto-Phase")
    with st.container(border=True):
        st.write(f"Koalition: **{game.coalition_party}**")
    passed_titles = [l["title"] for l in st.session_state.passed_this_round]
    
    if not game.veto_used and passed_titles:
        st.write("Der Kanzler kann ein Gesetz annullieren.")
        veto_law = st.selectbox("Wähle ein Gesetz für das Veto", ["Nicht verwenden"] + passed_titles)
        if st.button("RUNDE BEENDEN", use_container_width=True):
            finish_veto(veto_law)
    else:
        st.info("Veto nicht verfügbar oder keine Gesetze verabschiedet.")
        if st.button("WEITER", use_container_width=True):
            finish_veto("Nicht verwenden")

def finish_veto(veto_law):
    game = st.session_state.game
    final_laws = st.session_state.passed_this_round
    if veto_law != "Nicht verwenden":
        final_laws = [l for l in final_laws if l["title"] != veto_law]
        game.veto_used = True
    
    if "round_reports" not in st.session_state:
        st.session_state.round_reports = []
    if not final_laws:
        st.session_state.round_reports.append(game.handle_no_laws())
    else:
        for l in final_laws:
            st.session_state.round_reports.append(game.apply_law(l["id"]))
    
    game.current_round += 1
    st.session_state.step = "round_feedback"
    st.rerun()

def render_round_feedback():
    st.header("📈 Rating-Dynamik")
    game = st.session_state.game
    
    if "round_reports" in st.session_state:
        for report in st.session_state.round_reports:
            if report:
                with st.container(border=True):
                    if "law_title" in report:
                        st.subheader(f"📜 {report['law_title']}")
                    for effect in report["effects"]:
                        if "🌍" in effect: st.success(effect.replace("Позитивна міжнародна реакція", "Positive internationale Reaktion").replace("Негативна міжнародна реакція", "Negative internationale Reaktion"))
                        elif "⚠️" in effect or "❌" in effect: st.error(effect.replace("Скандул в уряді", "Regierungsskandal").replace("Скандал в уряді", "Regierungsskandal").replace("Випадковий корупційний скандал", "Zufälliger Korruptionsskandal"))
                        else: st.info(effect.replace("Опозиція знайшла слабке місце в законі", "Die Opposition hat eine Schwachstelle im Gesetz gefunden").replace("Імпакт закону", "Effekt des Gesetzes").replace("рейтинг коаліції знижений на 5 через відсутність нових законів", "Koalitionsrating um 5 gesenkt wegen fehlender Gesetze").replace("Жодних законів не прийнято", "Keine Gesetze verabschiedet"))

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric("Koalition", f"{game.ratings['coalition']:.1f}")
    with col2:
        with st.container(border=True):
            st.metric("Opposition", f"{game.ratings['opposition']:.1f}")
    
    btn_text = "NÄCHSTE RUNDE" if game.current_round <= game.max_rounds else "SPIEL BEENDEN"
    if st.button(btn_text, use_container_width=True):
        next_round_ui()

def render_end():
    st.markdown('<div class="hero-title fade-in">🏁 SPIEL BEENDET</div>', unsafe_allow_html=True)
    game = st.session_state.game
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f'<div style="text-align: center;"><h3>Koalition</h3><h1>{game.ratings["coalition"]:.1f}</h1></div>', unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown(f'<div style="text-align: center;"><h3>Opposition</h3><h1>{game.ratings["opposition"]:.1f}</h1></div>', unsafe_allow_html=True)
    
    if game.ratings["coalition"] > game.ratings["opposition"]:
        st.balloons()
        st.success("🎉 SIEG DER KOALITION!")
    else:
        st.success("🎉 SIEG DER OPPOSITION!")
    
    if st.button("NOCHMAL SPIELEN", use_container_width=True):
        st.session_state.clear()
        st.rerun()

SCREENS = {
    "splash": render_splash,
    "start": render_start,
    "setup": render_setup,
    "campaign": render_campaign,
    "roles_display": render_roles_display,
    "round": render_round,
    "veto_screen": render_veto_screen,
    "round_feedback": render_round_feedback,
    "end": render_end
}

if st.session_state.step in SCREENS:
    SCREENS[st.session_state.step]()
else:
    st.error("Unbekannter Spielzustand.")
