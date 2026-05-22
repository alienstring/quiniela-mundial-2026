import requests
from bs4 import BeautifulSoup
import re
import random
from database import get_db_connection, update_group_match_score, update_match_winner, get_matches

NAME_MAPPING = {
    "México": "México",
    "Sudáfrica": "Sudáfrica",
    "Corea del Sur": "Corea del Sur",
    "República Checa": "República Checa",
    "Canadá": "Canadá",
    "Bosnia y Herzegovina": "Bosnia y Herzegovina",
    "Bosnia": "Bosnia y Herzegovina",
    "Catar": "Catar",
    "Suiza": "Suiza",
    "Brasil": "Brasil",
    "Marruecos": "Marruecos",
    "Haití": "Haití",
    "Escocia": "Escocia",
    "Estados Unidos": "Estados Unidos",
    "EE. UU.": "Estados Unidos",
    "Paraguay": "Paraguay",
    "Australia": "Australia",
    "Turquía": "Turquía",
    "Alemania": "Alemania",
    "Curazao": "Curazao",
    "Costa de Marfil": "Costa de Marfil",
    "Ecuador": "Ecuador",
    "Países Bajos": "Países Bajos",
    "Holanda": "Países Bajos",
    "Japón": "Japón",
    "Suecia": "Suecia",
    "Túnez": "Túnez",
    "Bélgica": "Bélgica",
    "Egipto": "Egipto",
    "Irán": "Irán",
    "Nueva Zelanda": "Nueva Zelanda",
    "España": "España",
    "Cabo Verde": "Cabo Verde",
    "Arabia Saudita": "Arabia Saudita",
    "Arabia": "Arabia Saudita",
    "Uruguay": "Uruguay",
    "Francia": "Francia",
    "Senegal": "Senegal",
    "Irak": "Irak",
    "Noruega": "Noruega",
    "Argentina": "Argentina",
    "Argelia": "Argelia",
    "Austria": "Austria",
    "Jordania": "Jordania",
    "Portugal": "Portugal",
    "R. D. del Congo": "R. D. del Congo",
    "R.D. del Congo": "R. D. del Congo",
    "República Democrática del Congo": "R. D. del Congo",
    "Congo": "R. D. del Congo",
    "Uzbekistán": "Uzbekistán",
    "Colombia": "Colombia",
    "Inglaterra": "Inglaterra",
    "Croacia": "Croacia",
    "Ghana": "Ghana",
    "Panamá": "Panamá"
}

BILINGUAL_TEAM_MAP = {
    # English (API) -> Spanish (DB)
    "Mexico": "México",
    "South Africa": "Sudáfrica",
    "South Korea": "Corea del Sur",
    "Czech Republic": "República Checa",
    "Canada": "Canadá",
    "Bosnia & Herzegovina": "Bosnia y Herzegovina",
    "Bosnia and Herzegovina": "Bosnia y Herzegovina",
    "Bosnia": "Bosnia y Herzegovina",
    "Qatar": "Catar",
    "Switzerland": "Suiza",
    "Brazil": "Brasil",
    "Morocco": "Marruecos",
    "Haiti": "Haití",
    "Scotland": "Escocia",
    "USA": "Estados Unidos",
    "USA / United States": "Estados Unidos",
    "United States": "Estados Unidos",
    "Paraguay": "Paraguay",
    "Australia": "Australia",
    "Turkey": "Turquía",
    "Germany": "Alemania",
    "Curacao": "Curazao",
    "Ivory Coast": "Costa de Marfil",
    "Ecuador": "Ecuador",
    "Netherlands": "Países Bajos",
    "Japan": "Japón",
    "Sweden": "Suecia",
    "Tunisia": "Túnez",
    "Belgium": "Bélgica",
    "Egypt": "Egipto",
    "Iran": "Irán",
    "New Zealand": "Nueva Zelanda",
    "Spain": "España",
    "Cape Verde": "Cabo Verde",
    "Saudi Arabia": "Arabia Saudita",
    "Uruguay": "Uruguay",
    "France": "Francia",
    "Senegal": "Senegal",
    "Iraq": "Irak",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argelia",
    "Austria": "Austria",
    "Jordan": "Jordania",
    "Portugal": "Portugal",
    "DR Congo": "R. D. del Congo",
    "Democratic Republic of the Congo": "R. D. del Congo",
    "Congo DR": "R. D. del Congo",
    "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia",
    "England": "Inglaterra",
    "Croatia": "Croacia",
    "Ghana": "Ghana",
    "Panama": "Panamá"
}

WIKI_KNOCKOUT_MAP = {
    73: 1,    # Match 73: 2A vs 2B -> Match 1
    74: 2,    # Match 74: 1E vs 3ABCDF -> Match 2
    75: 3,    # Match 75: 1F vs 2C -> Match 3
    76: 4,    # Match 76: 1C vs 2F -> Match 4
    77: 5,    # Match 77: 1I vs 3CDFGH -> Match 5
    78: 6,    # Match 78: 2E vs 2I -> Match 6
    79: 7,    # Match 79: 1A vs 3CEFHI -> Match 7
    80: 8,    # Match 80: 1L vs 3EHIJK -> Match 8
    81: 10,   # Match 81: 1D vs 3BEFIJ -> Match 10
    82: 9,    # Match 82: 1G vs 3AEHIJ -> Match 9
    83: 12,   # Match 83: 2K vs 2L -> Match 12
    84: 11,   # Match 84: 1H vs 2J -> Match 11
    85: 13,   # Match 85: 1B vs 3EFGIJ -> Match 13
    86: 15,   # Match 86: 1J vs 2H -> Match 15
    87: 16,   # Match 87: 1K vs 3DEIJL -> Match 16
    88: 14,   # Match 88: 2D vs 2G -> Match 14
    
    # Round of 16 (89 to 96) -> Matches 17 to 24
    89: 17,
    90: 18,
    91: 19,
    92: 20,
    93: 21,
    94: 22,
    95: 23,
    96: 24,
    
    # Quarterfinals (97 to 100) -> Matches 25 to 28
    97: 25,
    98: 26,
    99: 27,
    100: 28,
    
    # Semifinals (101 to 102) -> Matches 29 to 30
    101: 29,
    102: 30,
    
    # Final (104) -> Match 31
    104: 31
}

def normalize_team_name(raw_name):
    if not raw_name:
        return None
    raw_cleaned = raw_name.strip()
    
    # Remove flags, emojis, and FIFA country codes like (MEX, USA, etc.)
    raw_cleaned = re.sub(r'^[A-Z]{3,4}\s+', '', raw_cleaned)
    raw_cleaned = re.sub(r'[^\w\s\.]', '', raw_cleaned).strip()
    
    for wiki_name, db_name in NAME_MAPPING.items():
        if wiki_name.lower() in raw_cleaned.lower():
            return db_name
    return None

def parse_score(score_text):
    """
    Parses scores from texts like '1 – 0', '2 - 1', '1:1', etc.
    Returns (score_a, score_b) as integers, or (None, None) if not played yet.
    """
    if not score_text:
        return None, None
    cleaned = score_text.strip()
    if "partido" in cleaned.lower() or "vs" in cleaned.lower() or "junio" in cleaned.lower():
        return None, None
        
    matches = re.findall(r'\d+', cleaned)
    if len(matches) >= 2:
        return int(matches[0]), int(matches[1])
    return None, None

def scrape_world_cup_results():
    """
    Scrapes Wikipedia for real-world FIFA 2026 match results.
    Matches are represented by table elements with class "vevent".
    """
    url = "https://es.wikipedia.org/wiki/Copa_Mundial_de_F%C3%BAtbol_de_2026"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False, f"Error al acceder a Wikipedia (Código {response.status_code})."
            
        soup = BeautifulSoup(response.content, 'html.parser')
        vevents = soup.find_all('table', class_="vevent")
        
        if not vevents:
            return False, "La Copa Mundial de la FIFA 2026 aún no ha comenzado (inicia el 11 de junio de 2026). Prueba con el botón 'Demo de Avance' para probar la sincronización simulada."
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Load teams by name to get IDs
        cursor.execute("SELECT id, name FROM teams")
        db_teams = {t["name"]: t["id"] for t in cursor.fetchall()}
        
        updated_groups_count = 0
        updated_bracket_count = 0
        
        for table_idx, v in enumerate(vevents):
            wiki_match_num = table_idx + 1
            
            tds = v.find_all('td')
            if len(tds) >= 4:
                team_a_raw = tds[1].text.strip()
                score_raw = tds[2].text.strip()
                team_b_raw = tds[3].text.strip()
                
                team_a_name = normalize_team_name(team_a_raw)
                team_b_name = normalize_team_name(team_b_raw)
                
                # Check if it's a group stage match
                if wiki_match_num <= 72:
                    score_a, score_b = parse_score(score_raw)
                    if score_a is None or score_b is None:
                        continue  # Not played yet
                        
                    cursor.execute(
                        "SELECT id, status, team_a_id, team_b_id FROM group_matches WHERE match_number = ?",
                        (wiki_match_num,)
                    )
                    gm_row = cursor.fetchone()
                    if gm_row:
                        gm_id = gm_row["id"]
                        curr_status = gm_row["status"]
                        if curr_status != 'Jugado':
                            db_t_a_id = gm_row["team_a_id"]
                            db_t_b_id = gm_row["team_b_id"]
                            
                            t_a_id_parsed = db_teams.get(team_a_name)
                            
                            # Determine order
                            if t_a_id_parsed == db_t_b_id:
                                s_a = score_b
                                s_b = score_a
                            else:
                                s_a = score_a
                                s_b = score_b
                                
                            cursor.execute(
                                "UPDATE group_matches SET score_a = ?, score_b = ?, status = 'Jugado' WHERE id = ?",
                                (s_a, s_b, gm_id)
                            )
                            updated_groups_count += 1
                            
                # Check if it's a knockout bracket match
                elif wiki_match_num in WIKI_KNOCKOUT_MAP:
                    m_num = WIKI_KNOCKOUT_MAP[wiki_match_num]
                    
                    t_a_id = db_teams.get(team_a_name) if team_a_name else None
                    t_b_id = db_teams.get(team_b_name) if team_b_name else None
                    
                    cursor.execute("SELECT team_a_id, team_b_id, winner_id FROM matches WHERE match_number = ?", (m_num,))
                    curr_match = cursor.fetchone()
                    
                    if curr_match:
                        # 1. Update team A/B IDs in database if qualified on Wikipedia but NULL in database
                        if t_a_id and curr_match["team_a_id"] != t_a_id:
                            cursor.execute("UPDATE matches SET team_a_id = ? WHERE match_number = ?", (t_a_id, m_num))
                            updated_bracket_count += 1
                        if t_b_id and curr_match["team_b_id"] != t_b_id:
                            cursor.execute("UPDATE matches SET team_b_id = ? WHERE match_number = ?", (t_b_id, m_num))
                            updated_bracket_count += 1
                            
                        # 2. Update score and winner if played
                        score_a, score_b = parse_score(score_raw)
                        if score_a is not None and score_b is not None:
                            curr_winner = curr_match["winner_id"]
                            if curr_winner is None:
                                is_a_bold = tds[1].find(['b', 'strong']) is not None
                                is_b_bold = tds[3].find(['b', 'strong']) is not None
                                
                                cursor.execute("SELECT team_a_id, team_b_id FROM matches WHERE match_number = ?", (m_num,))
                                fresh_match = cursor.fetchone()
                                actual_t_a_id = fresh_match["team_a_id"]
                                actual_t_b_id = fresh_match["team_b_id"]
                                
                                if actual_t_a_id and actual_t_b_id:
                                    winner_id = None
                                    if score_a > score_b:
                                        winner_id = actual_t_a_id
                                    elif score_b > score_a:
                                        winner_id = actual_t_b_id
                                    else:
                                        if is_a_bold:
                                            winner_id = actual_t_a_id
                                        elif is_b_bold:
                                            winner_id = actual_t_b_id
                                        else:
                                            winner_id = actual_t_a_id
                                            
                                    cursor.execute("UPDATE matches SET winner_id = ? WHERE match_number = ?", (winner_id, m_num))
                                    from database import propagate_match_change
                                    propagate_match_change(cursor, m_num)
                                    updated_bracket_count += 1
                        
        if updated_groups_count > 0 or updated_bracket_count > 0:
            from database import update_bracket_from_groups, recalculate_team_statuses
            update_bracket_from_groups(cursor)
            recalculate_team_statuses(cursor)
            
            conn.commit()
            conn.close()
            return True, f"🎉 Sincronización exitosa. Se actualizaron {updated_groups_count} partidos de fase de grupos y {updated_bracket_count} partidos de eliminatorias en vivo."
            
        conn.close()
        return False, "La Copa Mundial de la FIFA 2026 aún no tiene nuevos resultados en Wikipedia (inicia el 11 de junio de 2026). ¡Usa la 'Sincronización Simulada' para probar el avance automático!"
        
    except Exception as e:
        return False, f"Error en la sincronización automática: {str(e)}."

def simulate_next_match():
    """
    Simulates the next chronologically available unplayed match.
    Group stage matches (1-72) are completed first, followed by knockout matches as teams qualify.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Simulate unplayed group stage matches
    cursor.execute("""
        SELECT id, match_number, group_name, team_a_id, team_b_id 
        FROM group_matches 
        WHERE status = 'Pendiente' 
        ORDER BY match_number LIMIT 1
    """)
    unplayed_group = cursor.fetchone()
    
    if unplayed_group:
        score_a = random.randint(0, 4)
        score_b = random.randint(0, 4)
        
        gm_id = unplayed_group["id"]
        g_name = unplayed_group["group_name"]
        m_num = unplayed_group["match_number"]
        
        cursor.execute("SELECT name FROM teams WHERE id = ?", (unplayed_group["team_a_id"],))
        t_a_name = cursor.fetchone()["name"]
        
        cursor.execute("SELECT name FROM teams WHERE id = ?", (unplayed_group["team_b_id"],))
        t_b_name = cursor.fetchone()["name"]
        
        conn.close()
        
        success, msg = update_group_match_score(gm_id, score_a, score_b)
        if success:
            return True, f"Simulado Grupo {g_name} (Partido #{m_num}): **{t_a_name} {score_a} - {score_b} {t_b_name}**."
        return False, "Error al actualizar marcador de fase de grupos."
        
    # 2. Simulate bracket matches
    matches = get_matches()
    for m in matches:
        if m["team_a_id"] and m["team_b_id"] and not m["winner_id"]:
            winner_id = random.choice([m["team_a_id"], m["team_b_id"]])
            success, msg = update_match_winner(m["match_number"], winner_id)
            if success:
                winner_name = m["team_a_name"] if winner_id == m["team_a_id"] else m["team_b_name"]
                loser_name = m["team_b_name"] if winner_id == m["team_a_id"] else m["team_a_name"]
                return True, f"Simulado Partido #{m['match_number']} ({m['round']}): **{winner_name}** venció a **{loser_name}**."
            return False, msg
            
    conn.close()
    return False, "Todos los partidos disponibles ya han sido jugados u ocupan equipos que aún no se clasifican."

def simulate_full_tournament():
    """
    Simulates the entire tournament step-by-step until the final has been played.
    """
    played_count = 0
    max_iterations = 120  # Safe limit for 72 group + 31 bracket matches
    
    for _ in range(max_iterations):
        success, msg = simulate_next_match()
        if success:
            played_count += 1
        else:
            matches = get_matches()
            final_match = next((m for m in matches if m["match_number"] == 31), None)
            if final_match and final_match["winner_id"]:
                break
            elif played_count == 0:
                return False, "No hay partidos listos para jugarse. Asegúrate de inicializar los equipos y realizar el sorteo."
            else:
                break
                
    if played_count > 0:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM teams WHERE status = 'Campeón'")
        champion_row = cursor.fetchone()
        champion = champion_row["name"] if champion_row else "Desconocido"
        
        cursor.execute("SELECT name FROM teams WHERE status = 'Subcampeón'")
        runnerup_row = cursor.fetchone()
        runnerup = runnerup_row["name"] if runnerup_row else "Desconocido"
        conn.close()
        
        return True, f"¡Simulación completada con éxito! Se jugaron {played_count} partidos (Fase de Grupos y Eliminatorias).\n\n🏆 **Campeón: {champion}**\n🥈 **Subcampeón: {runnerup}**"
        
    return False, "El torneo ya ha finalizado. Por favor reinicia el torneo desde el panel de control si deseas volver a simular."

def sync_with_sports_api():
    """
    Sincroniza los resultados de los partidos reales del Mundial 2026 utilizando
    la API oficial de fútbol (API-Football) a través de RapidAPI.
    Busca la variable de entorno 'RAPIDAPI_KEY'. Si no está presente, retorna un fallo
    indicando cómo obtenerla, o delega al scraper si se desea un fallback transparente.
    """
    import os
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return False, "La clave de la API (RAPIDAPI_KEY) no está configurada en las variables de entorno."

    # API-Football Endpoint for Fixtures (League 1 is FIFA World Cup, Season is 2026)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    params = {
        "league": "1",
        "season": "2026"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            return False, f"Error al consultar la API de fútbol (Código HTTP {response.status_code})."

        res_data = response.json()
        fixtures = res_data.get("response", [])
        if not fixtures:
            return False, "La API retornó una respuesta vacía. Asegúrate de que la temporada 2026 esté disponible."

        conn = get_db_connection()
        cursor = conn.cursor()

        # Load teams by name to get IDs
        cursor.execute("SELECT id, name FROM teams")
        db_teams = {t["name"]: t["id"] for t in cursor.fetchall()}

        updated_count = 0

        # Create a translation helper
        def translate_team(english_name):
            return BILINGUAL_TEAM_MAP.get(english_name, english_name)

        for f in fixtures:
            fixture_status = f.get("fixture", {}).get("status", {})
            status_short = fixture_status.get("short")
            
            home_eng = f.get("teams", {}).get("home", {}).get("name")
            away_eng = f.get("teams", {}).get("away", {}).get("name")
            
            home_name = translate_team(home_eng)
            away_name = translate_team(away_eng)
            
            home_id = db_teams.get(home_name)
            away_id = db_teams.get(away_name)
            
            if not home_id or not away_id:
                continue

            # Check match status. FT, AET, PEN denote finished matches
            if status_short in ["FT", "AET", "PEN"]:
                score_home = f.get("goals", {}).get("home")
                score_away = f.get("goals", {}).get("away")
                
                if score_home is None or score_away is None:
                    continue

                # Try to find a group stage match matching home_id and away_id
                cursor.execute("""
                    SELECT id, score_a, score_b, status FROM group_matches 
                    WHERE (team_a_id = ? AND team_b_id = ?) OR (team_a_id = ? AND team_b_id = ?)
                """, (home_id, away_id, away_id, home_id))
                gm_row = cursor.fetchone()
                
                if gm_row:
                    gm_id = gm_row["id"]
                    db_score_a = gm_row["score_a"]
                    db_score_b = gm_row["score_b"]
                    db_status = gm_row["status"]
                    
                    # Decide order
                    cursor.execute("SELECT team_a_id FROM group_matches WHERE id = ?", (gm_id,))
                    t_a_id = cursor.fetchone()["team_a_id"]
                    
                    api_score_a = score_home if t_a_id == home_id else score_away
                    api_score_b = score_away if t_a_id == home_id else score_home

                    if db_status != 'Jugado' or db_score_a != api_score_a or db_score_b != api_score_b:
                        # update using our existing core logic
                        update_group_match_score(gm_id, api_score_a, api_score_b)
                        updated_count += 1
                else:
                    # Check if it's a bracket match
                    cursor.execute("""
                        SELECT match_number, team_a_id, team_b_id, winner_id FROM matches 
                        WHERE (team_a_id = ? AND team_b_id = ?) OR (team_a_id = ? AND team_b_id = ?)
                    """, (home_id, away_id, away_id, home_id))
                    m_row = cursor.fetchone()
                    if m_row:
                        m_num = m_row["match_number"]
                        winner_id = m_row["winner_id"]
                        
                        # Determine winner ID
                        home_win = f.get("teams", {}).get("home", {}).get("winner")
                        away_win = f.get("teams", {}).get("away", {}).get("winner")
                        
                        api_winner_id = home_id if home_win else (away_id if away_win else None)

                        if api_winner_id and winner_id != api_winner_id:
                            update_match_winner(m_num, api_winner_id)
                            updated_count += 1

        conn.close()
        
        if updated_count > 0:
            return True, f"Se han sincronizado y actualizado {updated_count} partidos reales a través de la API oficial."
        else:
            return True, "Los marcadores de la base de datos ya están al día con la API de fútbol real."

    except Exception as e:
        return False, f"Ocurrió un error inesperado al sincronizar con la API: {str(e)}"
