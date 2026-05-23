import streamlit as st
import pandas as pd
import time
import os
import database as db
import sync
import textwrap

# Page configuration
st.set_page_config(
    page_title="🏆 Quiniela Eliminatorias FIFA 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme & Custom Styles Injection
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    
    /* Ocultar barra superior y decoración de Streamlit, pero mantener el contenedor transparente */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Ocultar solo el menú de tres puntos y deploy de Streamlit en la cabecera */
    [data-testid="stHeader"] > div:first-child > div:first-child > div:nth-child(2) {
        display: none !important;
    }
    
    /* Botón flotante circular premium para reabrir el menú lateral (>>), visible siempre */
    [data-testid="collapsedControl"] {
        display: flex !important;
        background-color: #1E293B !important;
        border-radius: 50% !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
        position: fixed !important;
        left: 20px !important;
        top: 20px !important;
        z-index: 999999 !important;
        width: 42px !important;
        height: 42px !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        transform: scale(1.1) !important;
        background-color: #0F172A !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    footer {
        display: none !important;
    }
    
    /* Forzar modo oscuro absoluto en cada capa y contenedor del cuerpo principal */
    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stMain"], 
    .main, 
    [data-testid="stAppViewBlockContainer"], 
    .block-container,
    [data-testid="stVerticalBlock"] {
        background-color: #0E1117 !important;
        background: #0E1117 !important;
        color: #F8FAFC !important;
    }
    
    /* Forzar modo oscuro absoluto en la barra lateral */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarUserContent"], 
    .stSidebar {
        background-color: #1E293B !important;
        background: #1E293B !important;
        color: #F8FAFC !important;
    }
    
    html, body, [data-testid="stSidebar"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background & Glassmorphism Cards */
    .stApp {
        background-color: #0E1117;
    }
    
    .title-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        margin-bottom: 25px;
        text-align: center;
    }
    
    .financial-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .financial-card:hover {
        transform: translateY(-5px);
    }
    
    .card-gold {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.03) 100%);
        border: 1px solid rgba(255, 215, 0, 0.4);
        box-shadow: 0 8px 32px 0 rgba(255, 215, 0, 0.1);
    }
    
    .card-silver {
        background: linear-gradient(135deg, rgba(192, 192, 192, 0.15) 0%, rgba(192, 192, 192, 0.03) 100%);
        border: 1px solid rgba(192, 192, 192, 0.4);
        box-shadow: 0 8px 32px 0 rgba(192, 192, 192, 0.1);
    }
    
    .card-bronze {
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.15) 0%, rgba(205, 127, 50, 0.03) 100%);
        border: 1px solid rgba(205, 127, 50, 0.4);
        box-shadow: 0 8px 32px 0 rgba(205, 127, 50, 0.1);
    }
    
    .financial-title {
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .financial-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 6px;
    }
    
    .text-gold {
        color: #FFD700;
        text-shadow: 0 0 10px rgba(255,215,0,0.3);
    }
    
    .text-silver {
        color: #E2E8F0;
        text-shadow: 0 0 10px rgba(192,192,192,0.3);
    }
    
    .text-bronze {
        color: #CD7F32;
        text-shadow: 0 0 10px rgba(205,127,50,0.3);
    }
    
    .text-green {
        color: #10B981;
        text-shadow: 0 0 10px rgba(16,185,129,0.3);
    }
    
    /* Bracket styling */
    .bracket-match {
        background: #1E293B;
        border-radius: 10px;
        padding: 12px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    .bracket-team {
        display: flex;
        justify-content: space-between;
        padding: 4px 8px;
        border-radius: 6px;
        margin: 2px 0;
        font-size: 0.95rem;
    }
    
    .team-alive {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        font-weight: 600;
    }
    
    .team-eliminated {
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.15);
        color: #F87171;
        text-decoration: line-through;
        opacity: 0.65;
    }
    
    .team-pending {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(255,255,255,0.1);
        color: #64748B;
        font-style: italic;
    }
    
    .team-winner-match {
        border: 1px solid rgba(255, 215, 0, 0.5);
        background: rgba(255, 215, 0, 0.1);
        box-shadow: 0 0 10px rgba(255,215,0,0.15);
    }
    
    /* Group Match Card */
    .group-match-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Map team names to flag emojis and display names
TEAM_FLAGS = {
    "México": "🇲🇽 México",
    "Sudáfrica": "🇿🇦 Sudáfrica",
    "Corea del Sur": "🇰🇷 Corea del Sur",
    "República Checa": "🇨🇿 República Checa",
    "Canadá": "🇨🇦 Canadá",
    "Bosnia y Herzegovina": "🇧🇦 Bosnia y Herzegovina",
    "Catar": "🇶🇦 Catar",
    "Suiza": "🇨🇭 Suiza",
    "Brasil": "🇧🇷 Brasil",
    "Marruecos": "🇲🇦 Marruecos",
    "Haití": "🇭🇹 Haití",
    "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia",
    "Estados Unidos": "🇺🇸 Estados Unidos",
    "Paraguay": "🇵🇾 Paraguay",
    "Australia": "🇦🇺 Australia",
    "Turquía": "🇹🇷 Turquía",
    "Alemania": "🇩🇪 Alemania",
    "Curazao": "🇨🇼 Curazao",
    "Costa de Marfil": "🇨🇮 Costa de Marfil",
    "Ecuador": "🇪🇨 Ecuador",
    "Países Bajos": "🇳🇱 Países Bajos",
    "Japón": "🇯🇵 Japón",
    "Suecia": "🇸🇪 Suecia",
    "Túnez": "🇹🇳 Túnez",
    "Bélgica": "🇧🇪 Bélgica",
    "Egipto": "🇪🇬 Egipto",
    "Irán": "🇮🇷 Irán",
    "Nueva Zelanda": "🇳🇿 Nueva Zelanda",
    "España": "🇪🇸 España",
    "Cabo Verde": "🇨🇻 Cabo Verde",
    "Arabia Saudita": "🇸🇦 Arabia Saudita",
    "Uruguay": "🇺🇾 Uruguay",
    "Francia": "🇫🇷 Francia",
    "Senegal": "🇸🇳 Senegal",
    "Irak": "🇮🇶 Irak",
    "Noruega": "🇳🇴 Noruega",
    "Argentina": "🇦🇷 Argentina",
    "Argelia": "🇩🇿 Argelia",
    "Austria": "🇦🇹 Austria",
    "Jordania": "🇯🇴 Jordania",
    "Portugal": "🇵🇹 Portugal",
    "R. D. del Congo": "🇨🇩 R. D. del Congo",
    "Uzbekistán": "🇺🇿 Uzbekistán",
    "Colombia": "🇨🇴 Colombia",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra",
    "Croacia": "🇭🇷 Croacia",
    "Ghana": "🇬🇭 Ghana",
    "Panamá": "🇵🇦 Panamá"
}

# ISO 3166-1 alpha-2 codes for FlagCDN official images
TEAM_ISO_CODES = {
    "México": "mx",
    "Sudáfrica": "za",
    "Corea del Sur": "kr",
    "República Checa": "cz",
    "Canadá": "ca",
    "Bosnia y Herzegovina": "ba",
    "Catar": "qa",
    "Suiza": "ch",
    "Brasil": "br",
    "Marruecos": "ma",
    "Haití": "ht",
    "Escocia": "gb-sct",
    "Estados Unidos": "us",
    "Paraguay": "py",
    "Australia": "au",
    "Turquía": "tr",
    "Alemania": "de",
    "Curazao": "cw",
    "Costa de Marfil": "ci",
    "Ecuador": "ec",
    "Países Bajos": "nl",
    "Japón": "jp",
    "Suecia": "se",
    "Túnez": "tn",
    "Bélgica": "be",
    "Egipto": "eg",
    "Irán": "ir",
    "Nueva Zelanda": "nz",
    "España": "es",
    "Cabo Verde": "cv",
    "Arabia Saudita": "sa",
    "Uruguay": "uy",
    "Francia": "fr",
    "Senegal": "sn",
    "Irak": "iq",
    "Noruega": "no",
    "Argentina": "ar",
    "Argelia": "dz",
    "Austria": "at",
    "Jordania": "jo",
    "Portugal": "pt",
    "R. D. del Congo": "cd",
    "Uzbekistán": "uz",
    "Colombia": "co",
    "Inglaterra": "gb-eng",
    "Croacia": "hr",
    "Ghana": "gh",
    "Panamá": "pa"
}

def get_flag_url(team_name):
    if not team_name:
        return None
    iso = TEAM_ISO_CODES.get(team_name)
    if iso:
        return f"https://flagcdn.com/w40/{iso}.png"
    return None

def get_styled_team_plain(name, status, elim_round="N/A"):
    if not name:
        return "Pendiente"
    flag_name = TEAM_FLAGS.get(name, name)
    if status == 'Campeón':
        return f"🏆 {flag_name} (Campeón)"
    elif status == 'Subcampeón':
        return f"🥈 {flag_name} (Subcampeón)"
    elif pct_3rd > 0 and name == third_place_name:
        return f"🥉 {flag_name} (3er Lugar)"
    elif status == 'Eliminado':
        return f"❌ {flag_name} (Elim. en {elim_round})"
    else:
        return f"🟢 {flag_name}"

def get_styled_team_name_only(name, status, elim_round="N/A"):
    if not name:
        return "Pendiente"
    if status == 'Campeón':
        return f"🏆 {name} (Campeón)"
    elif status == 'Subcampeón':
        return f"🥈 {name} (Subcampeón)"
    elif pct_3rd > 0 and name == third_place_name:
        return f"🥉 {name} (3er Lugar)"
    elif status == 'Eliminado':
        return f"❌ {name} (Elim. en {elim_round})"
    else:
        return f"🟢 {name}"

def get_bracket_placeholder(match_number, slot):
    if 1 <= match_number <= 16:
        if slot == 'A':
            labels_a = {
                1: "Subcampeón A", 2: "Ganador E", 3: "Ganador F", 4: "Ganador C",
                5: "Ganador I", 6: "Subcampeón E", 7: "Ganador A", 8: "Ganador L",
                9: "Ganador G", 10: "Ganador D", 11: "Ganador H", 12: "Subcampeón K",
                13: "Ganador B", 14: "Subcampeón D", 15: "Ganador J", 16: "Ganador K"
            }
            return f"⏰ {labels_a.get(match_number, 'Pendiente')}"
        else:
            labels_b = {
                1: "Subcampeón B", 2: "Mejor 3ro #1", 3: "Subcampeón C", 4: "Subcampeón F",
                5: "Mejor 3ro #2", 6: "Subcampeón I", 7: "Mejor 3ro #3", 8: "Mejor 3ro #4",
                9: "Mejor 3ro #5", 10: "Mejor 3ro #6", 11: "Subcampeón J", 12: "Subcampeón L",
                13: "Mejor 3ro #7", 14: "Subcampeón G", 15: "Subcampeón H", 16: "Mejor 3ro #8"
            }
            return f"⏰ {labels_b.get(match_number, 'Pendiente')}"
    elif 17 <= match_number <= 24:
        octavos_map = {
            17: (2, 5), 18: (1, 3), 19: (4, 6), 20: (7, 8),
            21: (12, 11), 22: (10, 9), 23: (15, 14), 24: (13, 16)
        }
        src_a, src_b = octavos_map.get(match_number)
        src = src_a if slot == 'A' else src_b
        return f"⏰ Ganador M{src}"
    elif 25 <= match_number <= 28:
        cuartos_map = {
            25: (17, 18), 26: (21, 22), 27: (19, 20), 28: (23, 24)
        }
        src_a, src_b = cuartos_map.get(match_number)
        src = src_a if slot == 'A' else src_b
        return f"⏰ Ganador M{src}"
    elif 29 <= match_number <= 30:
        semis_map = {
            29: (25, 26), 30: (27, 28)
        }
        src_a, src_b = semis_map.get(match_number)
        src = src_a if slot == 'A' else src_b
        return f"⏰ Ganador M{src}"
    elif match_number == 31:
        return "⏰ Ganador M29" if slot == 'A' else "⏰ Ganador M30"
    return "⏰ Pendiente"

def get_bracket_team_label_html(name, slot, match_number):
    if not name:
        return f'<span style="color: #64748B; font-style: italic;">{get_bracket_placeholder(match_number, slot)}</span>'
    
    flag_url = get_flag_url(name)
    flag_img = f'<img src="{flag_url}" style="width: 20px; height: 15px; vertical-align: middle; margin-right: 8px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);">' if flag_url else ""
    return f'<span style="display: flex; align-items: center; justify-content: flex-start; color: inherit; font-weight: inherit;">{flag_img}{name}</span>'

# Ensure DB is initialized
db.init_db()

# Load Dynamic Financial configurations
try:
    player_cost = float(db.get_config("player_cost", "500"))
    pct_1st = float(db.get_config("pct_1st", "80"))
    pct_2nd = float(db.get_config("pct_2nd", "20"))
    pct_3rd = float(db.get_config("pct_3rd", "0"))
except Exception:
    player_cost = 500.0
    pct_1st = 80.0
    pct_2nd = 20.0
    pct_3rd = 0.0

players_list = db.get_players()
num_players = len(players_list) if players_list else 12

total_pot = num_players * player_cost
prize_1st = total_pot * (pct_1st / 100.0)
prize_2nd = total_pot * (pct_2nd / 100.0)
prize_3rd = total_pot * (pct_3rd / 100.0)

try:
    third_place_team = db.get_third_place_team()
    third_place_name = third_place_team["name"] if third_place_team else None
except Exception:
    third_place_name = None

# Sidebar Navigation
st.sidebar.markdown("<div style='text-align: center; font-size: 5rem; margin-bottom: 10px; margin-top: -20px;'>🏆</div>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: white; margin-top: 0px;'>Menú de Opciones</h2>", unsafe_allow_html=True)

# Initialize session state for admin login
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Sidebar Role Selector / Login Panel
st.sidebar.markdown('<div style="margin-top: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
role_selection = st.sidebar.selectbox(
    "🔑 Tipo de Acceso:",
    ["👤 Usuario Estándar", "🔐 Administrador"],
    index=1 if st.session_state.admin_logged_in else 0
)

# Process login/logout
if role_selection == "🔐 Administrador":
    if not st.session_state.admin_logged_in:
        admin_password = st.sidebar.text_input("Contraseña de Administrador:", type="password")
        if admin_password:
            if admin_password == "admin123":
                st.session_state.admin_logged_in = True
                st.sidebar.success("🔓 ¡Sesión iniciada como Admin!")
                st.rerun()
            else:
                st.sidebar.error("❌ Contraseña incorrecta")
    else:
        st.sidebar.markdown('<p style="color: #10B981; font-weight: 600; margin: 0 0 5px 0; text-align: center;">🔓 Sesión: Administrador</p>', unsafe_allow_html=True)
        if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()
else:
    if st.session_state.admin_logged_in:
        st.session_state.admin_logged_in = False
        st.rerun()

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Navigation Options based on login status
if st.session_state.admin_logged_in:
    menu_options = ["🏆 Tablero Principal", "🎲 Sorteo / Draft", "⚙️ Panel de Control"]
else:
    menu_options = ["🏆 Tablero Principal"]

page = st.sidebar.radio(
    "Selecciona una vista:",
    menu_options,
    index=0
)

# Header Banner
st.markdown("""
<div class="title-banner">
    <h1 style="color: #FFD700; margin: 0; font-size: 2.8rem; font-weight: 800; letter-spacing: 1px;">
        QUINIELA DE ELIMINATORIAS 2026
    </h1>
    <p style="color: #94A3B8; margin-top: 5px; font-size: 1.15rem; font-weight: 400;">
        Fase final del Mundial FIFA 2026 - Intranet Local
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------- PAGE 1: TABLERO PRINCIPAL -----------------
if page == "🏆 Tablero Principal":
    
    # Financial Metrics Section
    cols_to_render = ["pot"]
    if pct_1st > 0:
        cols_to_render.append("1st")
    if pct_2nd > 0:
        cols_to_render.append("2nd")
    if pct_3rd > 0:
        cols_to_render.append("3rd")

    cols = st.columns(len(cols_to_render))

    for idx, col_type in enumerate(cols_to_render):
        with cols[idx]:
            if col_type == "pot":
                st.markdown(f"""
                <div class="financial-card">
                    <div class="financial-title">💰 Botín Total</div>
                    <div class="financial-value text-green">${total_pot:,.2f}</div>
                    <div style="color: #64748B; font-size: 0.9rem;">{num_players} Jugadores × ${player_cost:,.2f} c/u</div>
                </div>
                """, unsafe_allow_html=True)
            elif col_type == "1st":
                st.markdown(f"""
                <div class="financial-card card-gold">
                    <div class="financial-title">🏆 Premio Campeón ({pct_1st:.0f}%)</div>
                    <div class="financial-value text-gold">${prize_1st:,.2f}</div>
                    <div style="color: #B45309; font-size: 0.9rem;">Dueño del Campeón Mundial</div>
                </div>
                """, unsafe_allow_html=True)
            elif col_type == "2nd":
                st.markdown(f"""
                <div class="financial-card card-silver">
                    <div class="financial-title">🥈 Premio Subcampeón ({pct_2nd:.0f}%)</div>
                    <div class="financial-value text-silver">${prize_2nd:,.2f}</div>
                    <div style="color: #475569; font-size: 0.9rem;">Dueño del Subcampeón</div>
                </div>
                """, unsafe_allow_html=True)
            elif col_type == "3rd":
                st.markdown(f"""
                <div class="financial-card card-bronze">
                    <div class="financial-title">🥉 Premio 3er Lugar ({pct_3rd:.0f}%)</div>
                    <div class="financial-value text-bronze">${prize_3rd:,.2f}</div>
                    <div style="color: #78350F; font-size: 0.9rem;">Mejor Semifinalista Eliminado</div>
                </div>
                """, unsafe_allow_html=True)

    # Tabs for different views in Dashboard
    tab_stands, tab_bracket_view, tab_group_matches_view = st.tabs([
        "📊 Estado de Jugadores", 
        "🌳 Bracket de Eliminatorias", 
        "⚽ Partidos Fase de Grupos"
    ])
    
    # Tab 1: Positions / Leaderboard
    with tab_stands:
        st.markdown("<h3 style='color: white; margin-top: 10px;'>📊 Posiciones y Participantes</h3>", unsafe_allow_html=True)
        
        assignments = db.get_assignments()
        
        if not assignments or not any(a["team1_name"] for a in assignments):
            st.info("⚠️ Los equipos aún no han sido sorteados o asignados. Dirígete a la pestaña **🎲 Sorteo / Draft** para iniciar el juego.")
        else:
            rows = []
            for a in assignments:
                states = [a["team1_status"], a["team2_status"]]
                
                # Dynamic combined earnings calculation
                total_player_earnings = 0.0
                prize_labels = []
                
                def eval_team_prize(t_name, t_status):
                    if not t_name:
                        return 0.0, ""
                    if t_status == 'Campeón' and pct_1st > 0:
                        return prize_1st, f"🏆 1er Lugar"
                    elif t_status == 'Subcampeón' and pct_2nd > 0:
                        return prize_2nd, f"🥈 2do Lugar"
                    elif pct_3rd > 0 and t_name == third_place_name:
                        return prize_3rd, f"🥉 3er Lugar"
                    return 0.0, ""
                
                e1, l1 = eval_team_prize(a["team1_name"], a["team1_status"])
                if e1 > 0:
                    total_player_earnings += e1
                    prize_labels.append(l1)
                
                e2, l2 = eval_team_prize(a["team2_name"], a["team2_status"])
                if e2 > 0:
                    total_player_earnings += e2
                    prize_labels.append(l2)
                
                if total_player_earnings > 0:
                    earnings = f"💰 **¡Ganó ${total_player_earnings:,.2f} pesos!** (" + " + ".join(prize_labels) + ")"
                    if 'Campeón' in states:
                        status_text = "🥇 ¡CAMPEÓN!"
                    elif 'Subcampeón' in states:
                        status_text = "🥈 ¡SUBCAMPEÓN!"
                    else:
                        status_text = "🥉 ¡3er LUGAR!"
                elif 'Vivo' in states:
                    count_alive = states.count('Vivo')
                    status_text = "🟢 En juego"
                    earnings = f"Continúa con {count_alive} equipo(s) vivo(s)"
                else:
                    status_text = "💀 Eliminado"
                    earnings = "Sin premio"
                    
                rows.append({
                    "Participante": a["player_name"],
                    "Equipo 1": get_styled_team_plain(a["team1_name"], a["team1_status"], a["team1_elim"]),
                    "Equipo 2": get_styled_team_plain(a["team2_name"], a["team2_status"], a["team2_elim"]),
                    "Estado del Jugador": status_text,
                    "Premio / Situación": earnings
                })
                
            def get_sort_order(row):
                if "🥇" in row["Estado del Jugador"]: return 0
                if "🥈" in row["Estado del Jugador"]: return 1
                if "🥉" in row["Estado del Jugador"]: return 2
                if "🟢" in row["Estado del Jugador"]: return 3
                return 4
                
            sorted_rows = sorted(rows, key=get_sort_order)
            
            table_html = """
<div style="overflow-x: auto; margin-top: 15px;">
  <table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.25); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); font-family: 'Outfit', sans-serif;">
    <thead>
      <tr style="background: rgba(15, 23, 42, 0.7); border-bottom: 1px solid rgba(255,255,255,0.08); color: #94A3B8; text-align: left; font-size: 0.95rem;">
        <th style="padding: 14px 16px; font-weight: 600;">Participante</th>
        <th style="padding: 14px 16px; font-weight: 600;">Selección 1</th>
        <th style="padding: 14px 16px; font-weight: 600;">Selección 2</th>
        <th style="padding: 14px 16px; font-weight: 600;">Estado</th>
        <th style="padding: 14px 16px; font-weight: 600;">Premio / Situación</th>
      </tr>
    </thead>
    <tbody style="color: #E2E8F0; font-size: 0.95rem;">
"""
            
            for row in sorted_rows:
                status_style = ""
                if "🥇" in row["Estado del Jugador"]:
                    status_style = "color: #FFD700; font-weight: bold;"
                elif "🥈" in row["Estado del Jugador"]:
                    status_style = "color: #E2E8F0; font-weight: bold;"
                elif "🥉" in row["Estado del Jugador"]:
                    status_style = "color: #CD7F32; font-weight: bold;"
                elif "🟢" in row["Estado del Jugador"]:
                    status_style = "color: #34D399; font-weight: bold;"
                else:
                    status_style = "color: #64748B; opacity: 0.8;"
                    
                table_html += f"""
<tr style="border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
  <td style="padding: 14px 16px; font-weight: 600; color: #FFFFFF;">{row["Participante"]}</td>
  <td style="padding: 14px 16px;">{row["Equipo 1"]}</td>
  <td style="padding: 14px 16px;">{row["Equipo 2"]}</td>
  <td style="padding: 14px 16px; {status_style}">{row["Estado del Jugador"]}</td>
  <td style="padding: 14px 16px; color: #94A3B8;">{row["Premio / Situación"]}</td>
</tr>
"""
                
            table_html += """
  </tbody>
</table>
</div>
"""
            st.markdown(table_html, unsafe_allow_html=True)
            
    # Tab 2: Elimination Bracket Tree
    with tab_bracket_view:
        st.markdown("<h3 style='color: white; margin-top: 10px;'>🌳 Árbol de Eliminación Directa</h3>", unsafe_allow_html=True)
        
        def get_bracket_placeholder(match_number, slot):
            if 1 <= match_number <= 16:
                if slot == 'A':
                    labels_a = {
                        1: "Subcampeón A", 2: "Ganador E", 3: "Ganador F", 4: "Ganador C",
                        5: "Ganador I", 6: "Subcampeón E", 7: "Ganador A", 8: "Ganador L",
                        9: "Ganador G", 10: "Ganador D", 11: "Ganador H", 12: "Subcampeón K",
                        13: "Ganador B", 14: "Subcampeón D", 15: "Ganador J", 16: "Ganador K"
                    }
                    return f"⏰ {labels_a.get(match_number, 'Pendiente')}"
                else:
                    labels_b = {
                        1: "Subcampeón B", 2: "Mejor 3ro #1", 3: "Subcampeón C", 4: "Subcampeón F",
                        5: "Mejor 3ro #2", 6: "Subcampeón I", 7: "Mejor 3ro #3", 8: "Mejor 3ro #4",
                        9: "Mejor 3ro #5", 10: "Mejor 3ro #6", 11: "Subcampeón J", 12: "Subcampeón L",
                        13: "Mejor 3ro #7", 14: "Subcampeón G", 15: "Subcampeón H", 16: "Mejor 3ro #8"
                    }
                    return f"⏰ {labels_b.get(match_number, 'Pendiente')}"
            elif 17 <= match_number <= 24:
                octavos_map = {
                    17: (2, 5),
                    18: (1, 3),
                    19: (4, 6),
                    20: (7, 8),
                    21: (12, 11),
                    22: (10, 9),
                    23: (15, 14),
                    24: (13, 16)
                }
                src_a, src_b = octavos_map.get(match_number)
                src = src_a if slot == 'A' else src_b
                return f"⏰ Ganador M{src}"
            elif 25 <= match_number <= 28:
                cuartos_map = {
                    25: (17, 18),
                    26: (21, 22),
                    27: (19, 20),
                    28: (23, 24)
                }
                src_a, src_b = cuartos_map.get(match_number)
                src = src_a if slot == 'A' else src_b
                return f"⏰ Ganador M{src}"
            elif 29 <= match_number <= 30:
                semis_map = {
                    29: (25, 26),
                    30: (27, 28)
                }
                src_a, src_b = semis_map.get(match_number)
                src = src_a if slot == 'A' else src_b
                return f"⏰ Ganador M{src}"
            elif match_number == 31:
                return "⏰ Ganador M29" if slot == 'A' else "⏰ Ganador M30"
            return "⏰ Pendiente"
            
        matches = db.get_matches()
        
        if not matches:
            st.warning("No hay partidos inicializados en el bracket.")
        else:
            r_32 = [m for m in matches if m["round"] == 'Dieciseisavos']
            r_16 = [m for m in matches if m["round"] == 'Octavos']
            r_8 = [m for m in matches if m["round"] == 'Cuartos']
            r_4 = [m for m in matches if m["round"] == 'Semifinales']
            r_2 = [m for m in matches if m["round"] == 'Final']
            
            c1, c2, c3, c4, c5 = st.columns(5)
            
            with c1:
                st.markdown("<h5 style='color: #94A3B8; text-align: center;'>Dieciseisavos</h5>", unsafe_allow_html=True)
                for m in r_32:
                    winner_style_a = "team-winner-match" if m["winner_id"] == m["team_a_id"] and m["winner_id"] else ""
                    winner_style_b = "team-winner-match" if m["winner_id"] == m["team_b_id"] and m["winner_id"] else ""
                    
                    status_a = "team-alive" if m["team_a_status"] == 'Vivo' else ("team-eliminated" if m["team_a_status"] == 'Eliminado' else "team-pending")
                    status_b = "team-alive" if m["team_b_status"] == 'Vivo' else ("team-eliminated" if m["team_b_status"] == 'Eliminado' else "team-pending")
                    
                    team_a_label = get_bracket_team_label_html(m['team_a_name'], 'A', m['match_number'])
                    team_b_label = get_bracket_team_label_html(m['team_b_name'], 'B', m['match_number'])
                    
                    st.markdown(f"""
                    <div class="bracket-match">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: bold; margin-bottom: 4px;">PARTIDO {m['match_number']}</div>
                        <div class="bracket-team {status_a} {winner_style_a}">
                            {team_a_label}
                        </div>
                        <div class="bracket-team {status_b} {winner_style_b}">
                            {team_b_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with c2:
                st.markdown("<h5 style='color: #94A3B8; text-align: center;'>Octavos</h5>", unsafe_allow_html=True)
                for m in r_16:
                    winner_style_a = "team-winner-match" if m["winner_id"] == m["team_a_id"] and m["winner_id"] else ""
                    winner_style_b = "team-winner-match" if m["winner_id"] == m["team_b_id"] and m["winner_id"] else ""
                    
                    status_a = "team-alive" if m["team_a_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_a_status"] == 'Eliminado' else "team-pending")
                    status_b = "team-alive" if m["team_b_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_b_status"] == 'Eliminado' else "team-pending")
                    
                    team_a_label = get_bracket_team_label_html(m['team_a_name'], 'A', m['match_number'])
                    team_b_label = get_bracket_team_label_html(m['team_b_name'], 'B', m['match_number'])
                    
                    st.markdown(f"""
                    <div class="bracket-match" style="margin-top: 30px;">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: bold; margin-bottom: 4px;">PARTIDO {m['match_number']}</div>
                        <div class="bracket-team {status_a} {winner_style_a}">
                            {team_a_label}
                        </div>
                        <div class="bracket-team {status_b} {winner_style_b}">
                            {team_b_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with c3:
                st.markdown("<h5 style='color: #94A3B8; text-align: center;'>Cuartos</h5>", unsafe_allow_html=True)
                for m in r_8:
                    winner_style_a = "team-winner-match" if m["winner_id"] == m["team_a_id"] and m["winner_id"] else ""
                    winner_style_b = "team-winner-match" if m["winner_id"] == m["team_b_id"] and m["winner_id"] else ""
                    
                    status_a = "team-alive" if m["team_a_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_a_status"] == 'Eliminado' else "team-pending")
                    status_b = "team-alive" if m["team_b_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_b_status"] == 'Eliminado' else "team-pending")
                    
                    team_a_label = get_bracket_team_label_html(m['team_a_name'], 'A', m['match_number'])
                    team_b_label = get_bracket_team_label_html(m['team_b_name'], 'B', m['match_number'])
                    
                    st.markdown(f"""
                    <div class="bracket-match" style="margin-top: 80px;">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: bold; margin-bottom: 4px;">PARTIDO {m['match_number']}</div>
                        <div class="bracket-team {status_a} {winner_style_a}">
                            {team_a_label}
                        </div>
                        <div class="bracket-team {status_b} {winner_style_b}">
                            {team_b_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with c4:
                st.markdown("<h5 style='color: #94A3B8; text-align: center;'>Semifinales</h5>", unsafe_allow_html=True)
                for m in r_4:
                    winner_style_a = "team-winner-match" if m["winner_id"] == m["team_a_id"] and m["winner_id"] else ""
                    winner_style_b = "team-winner-match" if m["winner_id"] == m["team_b_id"] and m["winner_id"] else ""
                    
                    status_a = "team-alive" if m["team_a_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_a_status"] == 'Eliminado' else "team-pending")
                    status_b = "team-alive" if m["team_b_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_b_status"] == 'Eliminado' else "team-pending")
                    
                    team_a_label = get_bracket_team_label_html(m['team_a_name'], 'A', m['match_number'])
                    team_b_label = get_bracket_team_label_html(m['team_b_name'], 'B', m['match_number'])
                    
                    st.markdown(f"""
                    <div class="bracket-match" style="margin-top: 170px;">
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: bold; margin-bottom: 4px;">PARTIDO {m['match_number']}</div>
                        <div class="bracket-team {status_a} {winner_style_a}">
                            {team_a_label}
                        </div>
                        <div class="bracket-team {status_b} {winner_style_b}">
                            {team_b_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with c5:
                st.markdown("<h5 style='color: #FFD700; text-align: center; font-weight: bold;'>Gran Final</h5>", unsafe_allow_html=True)
                for m in r_2:
                    winner_style_a = "team-winner-match" if m["winner_id"] == m["team_a_id"] and m["winner_id"] else ""
                    winner_style_b = "team-winner-match" if m["winner_id"] == m["team_b_id"] and m["winner_id"] else ""
                    
                    status_a = "team-alive" if m["team_a_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_a_status"] == 'Eliminado' else "team-pending")
                    status_b = "team-alive" if m["team_b_status"] in ['Vivo', 'Subcampeón', 'Campeón'] else ("team-eliminated" if m["team_b_status"] == 'Eliminado' else "team-pending")
                    
                    team_a_label = get_bracket_team_label_html(m['team_a_name'], 'A', m['match_number'])
                    team_b_label = get_bracket_team_label_html(m['team_b_name'], 'B', m['match_number'])
                    
                    st.markdown(f"""
                    <div class="bracket-match" style="margin-top: 320px; border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255,215,0,0.15);">
                        <div style="font-size: 0.75rem; color: #FFD700; font-weight: bold; margin-bottom: 6px; text-align: center;">🏆 GRAN FINAL 🏆</div>
                        <div class="bracket-team {status_a} {winner_style_a}">
                            {team_a_label}
                        </div>
                        <div class="bracket-team {status_b} {winner_style_b}">
                            {team_b_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Tab 3: Complete World Cup Group Stage Matches Calendar
    with tab_group_matches_view:
        st.markdown("<h3 style='color: white; margin-top: 10px;'>📅 Visor de Grupos y Calendario</h3>", unsafe_allow_html=True)
        st.write("Selecciona un grupo para visualizar su tabla de posiciones oficial y sus partidos de fase de grupos:")
        
        # 1. Group Selector
        group_selected = st.selectbox(
            "Selecciona un Grupo:", 
            options=[f"Grupo {g}" for g in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]]
        )
        g_letter = group_selected.split(" ")[1]
        
        # Fetch standings and statuses
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status, round_eliminated FROM teams")
        team_status_map = {row["id"]: (row["status"], row["round_eliminated"]) for row in cursor.fetchall()}
        standings = db.calculate_standings(cursor)
        conn.close()
        
        g_standings = standings.get(g_letter, [])
        
        col_table, col_fixtures = st.columns([5, 4])
        
        with col_table:
            st.markdown(f"##### 📊 Tabla de Posiciones - {group_selected}")
            if not g_standings:
                st.info("No hay datos disponibles para este grupo.")
            else:
                table_rows = []
                for idx, t_stats in enumerate(g_standings, 1):
                    t_id = t_stats["id"]
                    t_name = t_stats["name"]
                    status, elim_round = team_status_map.get(t_id, ("Vivo", "N/A"))
                    
                    flag_team = TEAM_FLAGS.get(t_name, t_name)
                    styled_team = get_styled_team_name_only(flag_team, status, elim_round)
                    
                    table_rows.append({
                        "Pos": idx,
                        "Equipo": styled_team,
                        "PJ": t_stats["pj"],
                        "PG": t_stats["pg"],
                        "PE": t_stats["pe"],
                        "PP": t_stats["pp"],
                        "GF": t_stats["gf"],
                        "GC": t_stats["gc"],
                        "GD": t_stats["dif"],
                        "PTS": t_stats["pts"]
                    })
                    
                group_table_html = """
<div style="overflow-x: auto; margin-top: 10px;">
  <table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.25); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); font-family: 'Outfit', sans-serif;">
    <thead>
      <tr style="background: rgba(15, 23, 42, 0.7); border-bottom: 1px solid rgba(255,255,255,0.08); color: #94A3B8; text-align: left; font-size: 0.9rem;">
        <th style="padding: 10px 12px; font-weight: 600; text-align: center; width: 40px;">Pos</th>
        <th style="padding: 10px 12px; font-weight: 600;">Equipo</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">PJ</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">G</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">E</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">P</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">GF</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">GC</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">GD</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center; color: #34D399;">PTS</th>
      </tr>
    </thead>
    <tbody style="color: #E2E8F0; font-size: 0.9rem;">
"""
                
                for row in table_rows:
                    group_table_html += f"""
<tr style="border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
  <td style="padding: 10px 12px; text-align: center; font-weight: 600; color: #94A3B8;">{row["Pos"]}</td>
  <td style="padding: 10px 12px; font-weight: 600; color: #FFFFFF;">{row["Equipo"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["PJ"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["PG"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["PE"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["PP"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["GF"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["GC"]}</td>
  <td style="padding: 10px 12px; text-align: center; font-weight: 600; color: { '#34D399' if row['GD'] > 0 else ('#F87171' if row['GD'] < 0 else '#94A3B8') };">{ '+' if row['GD'] > 0 else '' }{row["GD"]}</td>
  <td style="padding: 10px 12px; text-align: center; font-weight: bold; color: #34D399; background: rgba(16, 185, 129, 0.05);">{row["PTS"]}</td>
</tr>
"""
                    
                group_table_html += """
  </tbody>
</table>
</div>
"""
                st.markdown(group_table_html, unsafe_allow_html=True)
                
            # Render best third places dynamic ranking below
            st.markdown("##### 🏆 Tabla Comparativa de Terceros Lugares")
            st.write("Los **mejores 8** terceros lugares de los 12 grupos clasifican a la Ronda de 32:")
            
            best_thirds = db.get_best_third_places(standings)
            best_thirds_ids = {bt["id"] for bt in best_thirds}
            
            # Extract all 3rd places to show them complete with color code
            all_thirds = []
            for g_name, g_teams in standings.items():
                if len(g_teams) >= 3:
                    all_thirds.append(g_teams[2])
            
            # Sort all thirds
            all_thirds.sort(key=lambda x: (-x["pts"], -x["dif"], -x["gf"], x["name"]))
            
            thirds_rows = []
            for idx, t_stats in enumerate(all_thirds, 1):
                t_id = t_stats["id"]
                t_name = t_stats["name"]
                g_name = t_stats["group_name"]
                status, elim_round = team_status_map.get(t_id, ("Vivo", "N/A"))
                is_qualified = t_id in best_thirds_ids
                qual_emoji = "✅" if is_qualified else ("❌" if status == 'Eliminado' else "⏳")
                
                flag_t_name = TEAM_FLAGS.get(t_name, t_name)
                
                thirds_rows.append({
                    "Pos": idx,
                    "Grupo": f"Grupo {g_name}",
                    "Equipo": f"{qual_emoji} {flag_t_name}",
                    "PJ": t_stats["pj"],
                    "PTS": t_stats["pts"],
                    "GD": t_stats["dif"],
                    "GF": t_stats["gf"],
                    "Estado": "Clasificado" if is_qualified else ("Eliminado" if status == 'Eliminado' else "Pendiente")
                })
                
            if thirds_rows:
                thirds_table_html = """
<div style="overflow-x: auto; margin-top: 10px;">
  <table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.25); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); font-family: 'Outfit', sans-serif;">
    <thead>
      <tr style="background: rgba(15, 23, 42, 0.7); border-bottom: 1px solid rgba(255,255,255,0.08); color: #94A3B8; text-align: left; font-size: 0.9rem;">
        <th style="padding: 10px 12px; font-weight: 600; text-align: center; width: 40px;">Pos</th>
        <th style="padding: 10px 12px; font-weight: 600;">Grupo</th>
        <th style="padding: 10px 12px; font-weight: 600;">Equipo</th>
        <th style="padding: 10px 12px; text-align: center;">PJ</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center; color: #34D399;">PTS</th>
        <th style="padding: 10px 12px; text-align: center;">GD</th>
        <th style="padding: 10px 12px; text-align: center;">GF</th>
        <th style="padding: 10px 12px; font-weight: 600; text-align: center;">Estado</th>
      </tr>
    </thead>
    <tbody style="color: #E2E8F0; font-size: 0.9rem;">
"""
                
                for row in thirds_rows:
                    qual_bg = "background: rgba(16, 185, 129, 0.08);" if row["Estado"] == "Clasificado" else ("background: rgba(239, 68, 68, 0.04);" if row["Estado"] == "Eliminado" else "")
                    qual_color = "color: #34D399; font-weight: bold;" if row["Estado"] == "Clasificado" else ("color: #F87171; text-decoration: line-through; opacity: 0.7;" if row["Estado"] == "Eliminado" else "color: #94A3B8; font-style: italic;")
                    
                    thirds_table_html += f"""
<tr style="border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.2s; {qual_bg}" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
  <td style="padding: 10px 12px; text-align: center; font-weight: 600; color: #94A3B8;">{row["Pos"]}</td>
  <td style="padding: 10px 12px; font-weight: 600;">{row["Grupo"]}</td>
  <td style="padding: 10px 12px; font-weight: 600; color: #FFFFFF;">{row["Equipo"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["PJ"]}</td>
  <td style="padding: 10px 12px; text-align: center; font-weight: bold; color: #34D399;">{row["PTS"]}</td>
  <td style="padding: 10px 12px; text-align: center; font-weight: 600; color: { '#34D399' if row['GD'] > 0 else ('#F87171' if row['GD'] < 0 else '#94A3B8') };">{ '+' if row['GD'] > 0 else '' }{row["GD"]}</td>
  <td style="padding: 10px 12px; text-align: center;">{row["GF"]}</td>
  <td style="padding: 10px 12px; text-align: center; {qual_color}">{row["Estado"]}</td>
</tr>
"""
                    
                thirds_table_html += """
  </tbody>
</table>
</div>
"""
                st.markdown(thirds_table_html, unsafe_allow_html=True)
            else:
                st.info("Aún no se han jugado suficientes partidos para calcular los terceros lugares.")
                
        with col_fixtures:
            st.markdown(f"##### 📅 Partidos de {group_selected}")
            group_matches = db.get_group_matches()
            g_matches = [gm for gm in group_matches if gm["group_name"] == g_letter]
            
            if not g_matches:
                st.info("No hay partidos programados para este grupo.")
            else:
                for gm in g_matches:
                    flag_a_url = get_flag_url(gm["team_a_name"])
                    flag_b_url = get_flag_url(gm["team_b_name"])
                    
                    img_a = f'<img src="{flag_a_url}" style="width: 22px; height: 16px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);">' if flag_a_url else ''
                    img_b = f'<img src="{flag_b_url}" style="width: 22px; height: 16px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);">' if flag_b_url else ''
                    
                    t_a_html = f'<div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex: 1; font-weight: 600; color: white; font-size: 0.95rem; min-width: 0;"><span>{gm["team_a_name"]}</span> {img_a}</div>'
                    t_b_html = f'<div style="display: flex; align-items: center; justify-content: flex-start; gap: 8px; flex: 1; font-weight: 600; color: white; font-size: 0.95rem; min-width: 0;">{img_b} <span>{gm["team_b_name"]}</span></div>'
                    
                    if gm["status"] == 'Jugado':
                        score_text = f"<b style='font-size: 1.3rem; color: #10B981;'>{gm['score_a']} - {gm['score_b']}</b>"
                        card_border = "border-left: 5px solid #10B981;"
                        badge = "<span style='background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>JUGADO</span>"
                    else:
                        score_text = "<b style='color: #64748B; font-style: italic; font-size: 1.1rem;'>VS</b>"
                        card_border = "border-left: 5px solid #64748B;"
                        badge = "<span style='background: rgba(255, 255, 255, 0.05); color: #94A3B8; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>PENDIENTE</span>"
                        
                    st.markdown(f"""
                    <div class="group-match-card" style="{card_border} margin-bottom: 12px; padding: 15px;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94A3B8; margin-bottom: 6px;">
                            <span>Partido #{gm['match_number']}</span>
                            <div>
                                {badge}
                                <span style="margin-left: 8px;">📅 {gm['match_date']}</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; text-align: center;">
                            {t_a_html}
                            <div style="padding: 0 15px; min-width: 60px; text-align: center;">{score_text}</div>
                            {t_b_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ----------------- PAGE 2: SORTEO / DRAFT -----------------
elif page == "🎲 Sorteo / Draft":
    st.markdown("### 🎲 Sorteo y Asignación de Equipos")
    st.write("Cada uno de los 12 jugadores debe tener asignados exactamente 2 equipos únicos de los 24 clasificados a eliminación directa.")
    st.info("🎯 **Regla Especial de Competitividad:** El sorteo automático distribuye exclusivamente a los **24 mejores equipos del ranking oficial FIFA** real de entre los 48 participantes. Esto asegura que todos los jugadores reciban selecciones de alta calidad y el juego sea altamente competitivo y equilibrado.")
    
    players = db.get_players()
    teams = db.get_teams()
    assignments = db.get_assignments()
    
    # Dynamic calculation of Top 24 FIFA teams based on current database
    db_team_names = [t["name"] for t in teams]
    TOP_24_FIFA_TEAMS = db.get_top_24_qualified_teams(db_team_names)

    
    if len(players) != 12:
        st.warning(f"⚠️ Actualmente tienes registrados **{len(players)}/12 jugadores**. Se requieren exactamente 12 jugadores en la base de datos para realizar el sorteo. Registra jugadores en la pestaña **⚙️ Panel de Control**.")
    else:
        already_drafted = assignments and any(a["team1_name"] for a in assignments)
        
        tab_auto, tab_manual = st.tabs(["⚡ Sorteo Automático (Recomendado)", "✍️ Asignación Manual"])
        
        with tab_auto:
            if already_drafted:
                st.info("💡 Ya se ha realizado un sorteo. Al presionar el botón de abajo, se borrarán las asignaciones actuales y se hará un sorteo nuevo.")
                
            btn_start_sorteo = st.button("🔮 ¡Iniciar Sorteo Espectacular!", use_container_width=True)
            
            if btn_start_sorteo:
                db.clear_assignments()
                
                placeholder = st.empty()
                progress_bar = st.progress(0)
                
                import random
                bombo1 = TOP_24_FIFA_TEAMS[:12]
                bombo2 = TOP_24_FIFA_TEAMS[12:24]
                
                random.shuffle(bombo1)
                random.shuffle(bombo2)
                
                shuffled_teams = []
                for idx in range(12):
                    shuffled_teams.append(bombo1[idx])
                    shuffled_teams.append(bombo2[idx])
                
                temp_assignments = {}
                for idx, p in enumerate(players):
                    t1 = shuffled_teams[idx * 2]
                    t2 = shuffled_teams[idx * 2 + 1]
                    temp_assignments[p["name"]] = (t1, t2)

                
                for i in range(1, 101):
                    progress_bar.progress(i / 100)
                    temp_player = players[(i - 1) % len(players)]["name"]
                    temp_team = shuffled_teams[random.randint(0, 23)]
                    
                    temp_flag = get_flag_url(temp_team)
                    temp_flag_img = f'<div style="margin: 15px 0;"><img src="{temp_flag}" style="width: 80px; height: 56px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.2);"></div>' if temp_flag else ''
                    
                    placeholder.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.85); border: 2px solid #FFD700; border-radius: 16px; padding: 30px; text-align: center; backdrop-filter: blur(10px); box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
                        <h4 style="color: #94A3B8; margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;">🔮 Girando la tómbola...</h4>
                        {temp_flag_img}
                        <h1 style="color: #FFD700; font-size: 2.8rem; margin: 10px 0; font-weight: 800; text-shadow: 0 0 15px rgba(255,215,0,0.4);">⚡ {temp_team} ⚡</h1>
                        <p style="color: #E2E8F0; font-size: 1.25rem;">Asignando boleto para: <b style="color: #10B981; font-size: 1.4rem;">{temp_player}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.03)
                
                success, msg = db.make_random_draft()
                if success:
                    st.balloons()
                    placeholder.empty()
                    st.success("🎉 ¡Sorteo finalizado con éxito! Todos los jugadores han recibido sus equipos.")
                    
                    st.markdown("### 📋 Resultados del Sorteo")
                    cols = st.columns(3)
                    new_assignments = db.get_assignments()
                    for idx, a in enumerate(new_assignments):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            f1_url = get_flag_url(a['team1_name'])
                            f2_url = get_flag_url(a['team2_name'])
                            
                            img_1 = f'<img src="{f1_url}" style="width: 20px; height: 14px; border-radius: 2px; margin-right: 8px; vertical-align: middle; box-shadow: 0 1px 2px rgba(0,0,0,0.3);">' if f1_url else ''
                            img_2 = f'<img src="{f2_url}" style="width: 20px; height: 14px; border-radius: 2px; margin-right: 8px; vertical-align: middle; box-shadow: 0 1px 2px rgba(0,0,0,0.3);">' if f2_url else ''
                            
                            t1_html = f'<div style="display: flex; align-items: center; gap: 4px; font-size: 1rem; color: #34D399; margin: 4px 0;">{img_1}<span>{a["team1_name"]}</span></div>'
                            t2_html = f'<div style="display: flex; align-items: center; gap: 4px; font-size: 1rem; color: #34D399; margin: 4px 0;">{img_2}<span>{a["team2_name"]}</span></div>'
                            st.markdown(f"""
                            <div style="background: #1E293B; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #10B981;">
                                <h4 style="color: white; margin: 0 0 8px 0;">👤 {a['player_name']}</h4>
                                {t1_html}
                                {t2_html}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(msg)
                    
        with tab_manual:
            st.write("Si hicieron un sorteo físico (presencial con dados o tómbola real), puedes registrar manualmente los equipos de cada jugador:")
            
            with st.form("manual_draft_form"):
                draft_data = []
                # Provide teams with flag labels for beautiful dropdown select box
                available_teams = [t["name"] for t in teams]
                available_team_labels = [TEAM_FLAGS.get(t["name"], t["name"]) for t in teams]
                label_to_name = {TEAM_FLAGS.get(t["name"], t["name"]): t["name"] for t in teams}
                
                st.write("Selecciona los 2 equipos para cada uno de los 12 participantes:")
                
                cols_form = st.columns(2)
                
                for idx, p in enumerate(players):
                    col_form_idx = idx % 2
                    with cols_form[col_form_idx]:
                        st.markdown(f"##### 👤 {p['name']}")
                        
                        curr_t1 = next((a["team1_name"] for a in assignments if a["player_id"] == p["id"]), None)
                        curr_t2 = next((a["team2_name"] for a in assignments if a["player_id"] == p["id"]), None)
                        
                        idx_t1 = available_teams.index(curr_t1) if curr_t1 in available_teams else 0
                        idx_t2 = available_teams.index(curr_t2) if curr_t2 in available_teams else 1
                        
                        sel_t1_label = st.selectbox(
                            f"Equipo 1 para {p['name']}",
                            options=available_team_labels,
                            index=idx_t1,
                            key=f"p_{p['id']}_t1",
                            label_visibility="collapsed"
                        )
                        sel_t2_label = st.selectbox(
                            f"Equipo 2 para {p['name']}",
                            options=available_team_labels,
                            index=idx_t2,
                            key=f"p_{p['id']}_t2",
                            label_visibility="collapsed"
                        )
                        
                        sel_t1 = label_to_name[sel_t1_label]
                        sel_t2 = label_to_name[sel_t2_label]
                        
                        t1_id = next(t["id"] for t in teams if t["name"] == sel_t1)
                        t2_id = next(t["id"] for t in teams if t["name"] == sel_t2)
                        
                        draft_data.append({
                            "player_id": p["id"],
                            "team_ids": [t1_id, t2_id]
                        })
                        st.markdown("---")
                        
                btn_save_manual = st.form_submit_button("💾 Guardar Asignaciones Manuales", use_container_width=True)
                
                if btn_save_manual:
                    all_selected_teams = []
                    for d in draft_data:
                        all_selected_teams.extend(d["team_ids"])
                        
                    if len(set(all_selected_teams)) != 24:
                        st.error("❌ Error de Validación: Los 24 equipos deben ser asignados de forma exclusiva. Hay equipos repetidos entre jugadores. Cada equipo debe tener exactamente 1 dueño.")
                    else:
                        db.assign_teams_manually(draft_data)
                        st.success("🎉 ¡Asignaciones manuales registradas correctamente!")
                        st.balloons()

# ----------------- PAGE 3: PANEL DE CONTROL ADMINISTRADOR -----------------
elif page == "⚙️ Panel de Control":
    st.markdown("### ⚙️ Panel de Control Administrador")
    
    tab_players, tab_finance, tab_groups, tab_simulation, tab_sync, tab_db = st.tabs([
        "👥 Gestionar Jugadores", 
        "💰 Configuración de Premios",
        "⚽ Fase de Grupos",
        "🎲 Simulador de Torneo", 
        "🔄 Sincronización en Tiempo Real",
        "⚠️ Configuración de Base de Datos"
    ])
    
    # 1. PLAYERS MANAGEMENT
    with tab_players:
        st.markdown("#### 👥 Jugadores Registrados")
        st.write(f"Para el botín completo (${total_pot:,.2f} pesos) se requiere registrar exactamente 12 jugadores:")
        
        players = db.get_players()
        st.write(f"Jugadores registrados actualmente: **{len(players)} / 12**")
        
        cols_players = st.columns(4)
        for idx, p in enumerate(players):
            col_p = cols_players[idx % 4]
            with col_p:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: white;">{p['name']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Eliminar a {p['name']}", key=f"del_{p['id']}"):
                    db.delete_player(p["id"])
                    st.rerun()
                    
        st.markdown("##### ➕ Agregar Nuevo Jugador")
        with st.form("add_player_form"):
            new_name = st.text_input("Nombre del Participante:")
            btn_add = st.form_submit_button("Agregar Jugador")
            
            if btn_add:
                if not new_name.strip():
                    st.error("El nombre no puede estar vacío.")
                elif len(players) >= 12:
                    st.error("Ya hay 12 jugadores registrados (límite para este juego).")
                else:
                    success = db.add_player(new_name)
                    if success:
                        st.success(f"¡Jugador '{new_name}' agregado!")
                        st.rerun()
                    else:
                        st.error("Este nombre de jugador ya existe.")
                        
    # 2. FINANCIAL & PRIZES CONFIGURATION
    with tab_finance:
        st.markdown("#### 💰 Configuración Financiera y de Premios")
        st.write("Establece la cuota por jugador y define cómo se repartirá el botín acumulado.")
        
        # Check if games have already started (at least one played match in group_matches or matches)
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM group_matches WHERE status = 'Jugado'")
            played_g = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM matches WHERE winner_id IS NOT NULL")
            played_m = cursor.fetchone()[0]
        except Exception:
            played_g = 0
            played_m = 0
        finally:
            conn.close()
        
        games_started = (played_g > 0 or played_m > 0)
        
        if games_started:
            st.warning("⚠️ **¡El torneo ya ha comenzado!** Modificar la configuración financiera en este punto puede generar inconsistencias si ya hay equipos eliminados o campeones definidos.")
            
        input_cost = st.number_input("💵 Cuota de Inscripción por Jugador ($):", min_value=0.0, value=player_cost, step=50.0)
        
        st.write("📈 **Distribución del Botín (%)**")
        st.write("La suma de los porcentajes de 1er, 2do y 3er lugar debe sumar exactamente **100%**.")
        
        input_pct_1st = st.number_input("🥇 Porcentaje 1er Lugar (%):", min_value=0.0, max_value=100.0, value=pct_1st, step=5.0)
        input_pct_2nd = st.number_input("🥈 Porcentaje 2do Lugar (%):", min_value=0.0, max_value=100.0, value=pct_2nd, step=5.0)
        input_pct_3rd = st.number_input("🥉 Porcentaje 3er Lugar (Opcional) (%):", min_value=0.0, max_value=100.0, value=pct_3rd, step=5.0)
        
        total_sum = input_pct_1st + input_pct_2nd + input_pct_3rd
        
        if total_sum == 100.0:
            st.success(f"✅ Suma de porcentajes correcta: **{total_sum:.0f}%**")
            allow_save = True
        else:
            st.error(f"❌ La suma de los porcentajes debe ser exactamente 100%. Actualmente suma **{total_sum:.0f}%**.")
            allow_save = False
            
        btn_save_finance = st.button("💾 Guardar Configuración Financiera", disabled=not allow_save, type="primary")
        
        if btn_save_finance and allow_save:
            db.set_config("player_cost", str(input_cost))
            db.set_config("pct_1st", str(input_pct_1st))
            db.set_config("pct_2nd", str(input_pct_2nd))
            db.set_config("pct_3rd", str(input_pct_3rd))
            st.success("🎉 ¡Configuración financiera guardada y aplicada con éxito!")
            time.sleep(1.5)
            st.rerun()

    # 3. GROUP STAGE ELIMINATIONS & MATCH RESULTS
    with tab_groups:
        st.markdown("#### ⚽ Administración - Fase de Grupos")
        st.write("Actualiza los marcadores de la fase de grupos o declara cuáles equipos fueron eliminados.")
        
        col_g_scores, col_g_elims = st.columns([1, 1])
        
        # Column A: Update Group Scores
        with col_g_scores:
            st.markdown("##### ✍️ Actualizar Marcador de Grupos")
            st.write("Registra los marcadores de los duelos de fase de grupos:")
            
            group_matches = db.get_group_matches()
            unplayed_g_matches = [gm for gm in group_matches if gm["status"] == 'Pendiente']
            
            if not unplayed_g_matches:
                st.info("Todos los partidos de fase de grupos ya han sido registrados. Si deseas cambiar algo, puedes reiniciar el torneo.")
            else:
                with st.form("group_score_form"):
                    match_options = [
                        f"Partido #{gm['match_number']} - Grupo {gm['group_name']} ({gm['match_date']}): {gm['team_a_name']} vs {gm['team_b_name']}"
                        for gm in unplayed_g_matches
                    ]
                    selected_gm_label = st.selectbox(
                        "Selecciona el partido a actualizar:",
                        options=match_options
                    )
                    
                    selected_idx = match_options.index(selected_gm_label)
                    gm_obj = unplayed_g_matches[selected_idx]
                    
                    col_score_a, col_score_b = st.columns(2)
                    with col_score_a:
                        score_a = st.number_input(f"Goles {gm_obj['team_a_name']}:", min_value=0, value=0, step=1)
                    with col_score_b:
                        score_b = st.number_input(f"Goles {gm_obj['team_b_name']}:", min_value=0, value=0, step=1)
                        
                    btn_save_g_score = st.form_submit_button("💾 Guardar Marcador")
                    
                    if btn_save_g_score:
                        success, msg = db.update_group_match_score(gm_obj["id"], score_a, score_b)
                        if success:
                            st.success(f"Marcador registrado: **{gm_obj['team_a_name']} {score_a} - {score_b} {gm_obj['team_b_name']}**")
                            time.sleep(1)
                            st.rerun()
                            
        # Column B: Eliminate Teams in Group Stage
        with col_g_elims:
            st.markdown("##### ❌ Eliminar Equipos de Fase de Grupos")
            st.write("Si necesitas forzar la eliminación manual de un equipo de la fase de grupos:")
            
            group_sel_elim = st.selectbox(
                "Selecciona el Grupo del equipo:",
                options=[f"Grupo {g}" for g in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]],
                key="group_sel_elim"
            )
            g_letter_elim = group_sel_elim.split(" ")[1]
            
            teams = db.get_teams()
            g_teams_elim = [t for t in teams if t["group_name"] == g_letter_elim]
            
            for t in g_teams_elim:
                flag_url = get_flag_url(t["name"])
                img_tag = f'<img src="{flag_url}" style="width: 20px; height: 14px; border-radius: 2px; margin-right: 8px; vertical-align: middle; box-shadow: 0 1px 2px rgba(0,0,0,0.2);">' if flag_url else ''
                
                if t["status"] == 'Eliminado':
                    st.markdown(f'<div style="color: #EF4444; text-decoration: line-through; display: flex; align-items: center; gap: 4px; font-weight: 500; margin-bottom: 8px;">❌ {img_tag} {t["name"]} <span style="font-size: 0.85rem; color: #F87171; font-style: italic; text-decoration: none; margin-left: 5px;">({t["round_eliminated"]})</span></div>', unsafe_allow_html=True)
                else:
                    col_team_name, col_team_btn = st.columns([2, 1])
                    with col_team_name:
                        st.markdown(f'<div style="color: #10B981; display: flex; align-items: center; gap: 4px; font-weight: 600; padding: 4px 0;">🟢 {img_tag} {t["name"]}</div>', unsafe_allow_html=True)
                    with col_team_btn:
                        if st.button("❌ Eliminar", key=f"elim_g_{t['id']}"):
                            success, msg = db.eliminate_in_group_stage(t["id"])
                            if success:
                                st.success(f"{t['name']} eliminado")
                                time.sleep(1.5)
                                st.rerun()

    # 4. TOURNAMENT SIMULATOR
    with tab_simulation:
        st.markdown("#### 🎲 Simulador del Torneo (Modo Demo / Pruebas)")
        st.write(f"Avanza los partidos del bracket de forma aleatoria para probar el flujo de eliminatorias y ver cómo se ganan los ${total_pot:,.2f} pesos.")
        
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            st.markdown("##### ⚡ Simular Siguiente Partido")
            st.write("Juega el siguiente partido disponible en orden cronológico.")
            btn_sim_next = st.button("🎲 Jugar Siguiente Partido")
            
            if btn_sim_next:
                success, msg = sync.simulate_next_match()
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
                    
        with col_sim2:
            st.markdown("##### 🏆 Simular Todo el Torneo")
            st.write("Simula de golpe todos los partidos restantes hasta coronar al Campeón.")
            btn_sim_all = st.button("👑 Simular Torneo Completo")
            
            if btn_sim_all:
                success, msg = sync.simulate_full_tournament()
                if success:
                    st.success(msg)
                    st.balloons()
                    st.snow()
                else:
                    st.error(msg)
                    
        st.markdown("---")
        st.markdown("#### ✍️ Registro Manual de Ganadores")
        st.write("Actualiza de forma manual qué equipo ganó cualquier partido del bracket en la vida real.")
        
        matches = db.get_matches()
        unplayed_matches = [m for m in matches if m["team_a_name"] and m["team_b_name"] and not m["winner_id"]]
        
        if not unplayed_matches:
            st.info("No hay partidos activos y listos para jugarse. Asegúrate de inicializar los equipos y avanzar en el torneo.")
        else:
            with st.form("manual_winner_form"):
                match_options = [
                    f"Partido #{m['match_number']} ({m['round']}): {m['team_a_name']} vs {m['team_b_name']}"
                    for m in unplayed_matches
                ]
                selected_match_label = st.selectbox(
                    "Selecciona el partido a resolver:",
                    options=match_options
                )
                
                selected_idx = match_options.index(selected_match_label)
                match_obj = unplayed_matches[selected_idx]
                match_num = match_obj["match_number"]
                
                selected_winner = st.radio(
                    "Selecciona el equipo ganador:",
                    options=[match_obj["team_a_name"], match_obj["team_b_name"]]
                )
                
                btn_save_winner = st.form_submit_button("💾 Guardar Ganador")
                
                if btn_save_winner:
                    winner_id = match_obj["team_a_id"] if selected_winner == match_obj["team_a_name"] else match_obj["team_b_id"]
                    success, msg = db.update_match_winner(match_num, winner_id)
                    if success:
                        st.success(f"🏆 Se registró la victoria de **{selected_winner}** en el Partido {match_num}.")
                        if match_num == 31:
                            st.balloons()
                            st.snow()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                        
    # 5. REAL-TIME SYNC
    with tab_sync:
        st.markdown("#### 🔄 Sincronización Automática de Resultados")
        st.write("Mantén el torneo actualizado con los marcadores oficiales y el avance real de la Copa del Mundo FIFA 2026.")
        
        # Display Environment Database Status
        db_status_color = "#10B981" if db.USING_POSTGRES else "#3B82F6"
        db_status_text = "🟢 Conectado a PostgreSQL (Base de Datos en la Nube)" if db.USING_POSTGRES else "🔵 Conectado a SQLite (Base de Datos Local)"
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
            <h5 style="color: white; margin-top: 0; margin-bottom: 10px;">🛡️ Estado del Servidor y Datos</h5>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 600; color: #94A3B8; font-size: 0.95rem;">Base de datos activa:</span>
                    <span style="color: {db_status_color}; font-weight: 700; font-size: 0.95rem;">{db_status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        import os
        api_key_configured = os.environ.get("RAPIDAPI_KEY") is not None
        
        col_sync_api, col_sync_wiki = st.columns(2)
        
        with col_sync_api:
            st.markdown("##### 🚀 API Deportiva Profesional (En Vivo)")
            st.write("Sincroniza directamente con los servidores de **API-Football** de forma ultra-rápida y confiable.")
            
            if api_key_configured:
                st.success("🟢 API Key detectada en las variables de entorno.")
            else:
                st.info("💡 **Sin API Key**: Para usar el servicio en vivo, configura la variable de entorno `RAPIDAPI_KEY` en tu hosting.")
                
            btn_sync_api = st.button("🔌 Sincronizar vía API Deportiva (Recomendado)", use_container_width=True, type="primary")
            if btn_sync_api:
                if not api_key_configured:
                    st.error("❌ No se encontró la clave de API `RAPIDAPI_KEY`. Por favor, configúrala o utiliza el respaldo de Wikipedia.")
                else:
                    with st.spinner("Sincronizando marcadores reales en vivo..."):
                        success, msg = sync.sync_with_sports_api()
                        if success:
                            st.success(msg)
                            st.balloons()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(msg)
                            
        with col_sync_wiki:
            st.markdown("##### 🌐 Wikipedia Web Scraper (Respaldo)")
            st.write("Lee y procesa las tablas del artículo en español de la Copa Mundial 2026 de forma automatizada.")
            st.warning("⚠️ **Nota**: Puede verse afectado si cambian el formato del diseño de la página de Wikipedia.")
            
            btn_sync_wiki = st.button("🌐 Sincronizar vía Wikipedia (Fallback)", use_container_width=True)
            if btn_sync_wiki:
                with st.spinner("Escaneando el portal de Wikipedia en tiempo real..."):
                    success, msg = sync.scrape_world_cup_results()
                    if success:
                        st.success(msg)
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.warning(msg)
                    
    # 6. DATABASE CONFIG
    with tab_db:
        st.markdown("#### ⚠️ Configuración y Reinicios")
        st.write("Herramientas para restablecer el juego a su estado original o borrar la información de pruebas:")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("##### 🏆 Restablecer Torneo")
            st.write("Vuelve a colocar a todos los 24 equipos como **Vivos** y borra el progreso de los partidos en el bracket. Las asignaciones de jugadores y equipos **se conservan**.")
            btn_reset_bracket = st.button("🔄 Restablecer Bracket (Mantener Sorteo)", type="secondary")
            
            if btn_reset_bracket:
                success, msg = db.reset_tournament_brackets()
                if success:
                    st.success(msg)
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(msg)
                    
        with col_res2:
            st.markdown("##### 🚨 Reinicio Total de Fábrica")
            st.write("Borrara absolutamente todos los datos: jugadores, equipos clasificados, asignaciones de sorteo y partidos. Restablecerá la base de datos a sus valores iniciales por defecto.")
            btn_reset_all = st.button("🚨 Reiniciar Base de Datos Completamente", type="primary")
            
            if btn_reset_all:
                db.init_db(reset=True)
                st.success("🔥 ¡Base de datos reiniciada con éxito de fábrica!")
                time.sleep(1.5)
                st.rerun()
