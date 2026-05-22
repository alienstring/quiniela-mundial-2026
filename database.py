import sqlite3
import random
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiniela_2026.db')

MATCH_PROPAGATION = {
    # Round of 32 (1 to 16) -> Round of 16 (17 to 24)
    1: (18, 'A'),   # Winner 1 goes to Match 18, Slot A
    3: (18, 'B'),   # Winner 3 goes to Match 18, Slot B
    
    2: (17, 'A'),   # Winner 2 goes to Match 17, Slot A
    5: (17, 'B'),   # Winner 5 goes to Match 17, Slot B
    
    4: (19, 'A'),   # Winner 4 goes to Match 19, Slot A
    6: (19, 'B'),   # Winner 6 goes to Match 19, Slot B
    
    7: (20, 'A'),   # Winner 7 goes to Match 20, Slot A
    8: (20, 'B'),   # Winner 8 goes to Match 20, Slot B
    
    12: (21, 'A'),  # Winner 12 goes to Match 21, Slot A
    11: (21, 'B'),  # Winner 11 goes to Match 21, Slot B
    
    10: (22, 'A'),  # Winner 10 goes to Match 22, Slot A
    9: (22, 'B'),   # Winner 9 goes to Match 22, Slot B
    
    15: (23, 'A'),  # Winner 15 goes to Match 23, Slot A
    14: (23, 'B'),  # Winner 14 goes to Match 23, Slot B
    
    13: (24, 'A'),  # Winner 13 goes to Match 24, Slot A
    16: (24, 'B'),  # Winner 16 goes to Match 24, Slot B
    
    # Round of 16 (17 to 24) -> Quarterfinals (25 to 28)
    17: (25, 'A'),  # Winner 17 goes to Match 25, Slot A
    18: (25, 'B'),  # Winner 18 goes to Match 25, Slot B
    
    21: (26, 'A'),  # Winner 21 goes to Match 26, Slot A
    22: (26, 'B'),  # Winner 22 goes to Match 26, Slot B
    
    19: (27, 'A'),  # Winner 19 goes to Match 27, Slot A
    20: (27, 'B'),  # Winner 20 goes to Match 27, Slot B
    
    23: (28, 'A'),  # Winner 23 goes to Match 28, Slot A
    24: (28, 'B'),  # Winner 24 goes to Match 28, Slot B
    
    # Quarterfinals (25 to 28) -> Semifinals (29 to 30)
    25: (29, 'A'),  # Winner 25 goes to Match 29, Slot A
    26: (29, 'B'),  # Winner 26 goes to Match 29, Slot B
    
    27: (30, 'A'),  # Winner 27 goes to Match 30, Slot A
    28: (30, 'B'),  # Winner 28 goes to Match 30, Slot B
    
    # Semifinals (29 to 30) -> Final (31)
    29: (31, 'A'),  # Winner 29 goes to Match 31, Slot A
    30: (31, 'B')   # Winner 30 goes to Match 31, Slot B
}

DEFAULT_TEAMS = [
    # Group A
    {"name": "México", "group_name": "A"},
    {"name": "Sudáfrica", "group_name": "A"},
    {"name": "Corea del Sur", "group_name": "A"},
    {"name": "República Checa", "group_name": "A"},
    # Group B
    {"name": "Canadá", "group_name": "B"},
    {"name": "Bosnia y Herzegovina", "group_name": "B"},
    {"name": "Catar", "group_name": "B"},
    {"name": "Suiza", "group_name": "B"},
    # Group C
    {"name": "Brasil", "group_name": "C"},
    {"name": "Marruecos", "group_name": "C"},
    {"name": "Haití", "group_name": "C"},
    {"name": "Escocia", "group_name": "C"},
    # Group D
    {"name": "Estados Unidos", "group_name": "D"},
    {"name": "Paraguay", "group_name": "D"},
    {"name": "Australia", "group_name": "D"},
    {"name": "Turquía", "group_name": "D"},
    # Group E
    {"name": "Alemania", "group_name": "E"},
    {"name": "Curazao", "group_name": "E"},
    {"name": "Costa de Marfil", "group_name": "E"},
    {"name": "Ecuador", "group_name": "E"},
    # Group F
    {"name": "Países Bajos", "group_name": "F"},
    {"name": "Japón", "group_name": "F"},
    {"name": "Suecia", "group_name": "F"},
    {"name": "Túnez", "group_name": "F"},
    # Group G
    {"name": "Bélgica", "group_name": "G"},
    {"name": "Egipto", "group_name": "G"},
    {"name": "Irán", "group_name": "G"},
    {"name": "Nueva Zelanda", "group_name": "G"},
    # Group H
    {"name": "España", "group_name": "H"},
    {"name": "Cabo Verde", "group_name": "H"},
    {"name": "Arabia Saudita", "group_name": "H"},
    {"name": "Uruguay", "group_name": "H"},
    # Group I
    {"name": "Francia", "group_name": "I"},
    {"name": "Senegal", "group_name": "I"},
    {"name": "Irak", "group_name": "I"},
    {"name": "Noruega", "group_name": "I"},
    # Group J
    {"name": "Argentina", "group_name": "J"},
    {"name": "Argelia", "group_name": "J"},
    {"name": "Austria", "group_name": "J"},
    {"name": "Jordania", "group_name": "J"},
    # Group K
    {"name": "Portugal", "group_name": "K"},
    {"name": "R. D. del Congo", "group_name": "K"},
    {"name": "Uzbekistán", "group_name": "K"},
    {"name": "Colombia", "group_name": "K"},
    # Group L
    {"name": "Inglaterra", "group_name": "L"},
    {"name": "Croacia", "group_name": "L"},
    {"name": "Ghana", "group_name": "L"},
    {"name": "Panamá", "group_name": "L"}
]

GROUP_MATCHES_DEFS = [
    # Group A
    ("A", "México", "Sudáfrica", "11 de junio de 2026"),
    ("A", "Corea del Sur", "República Checa", "11 de junio de 2026"),
    ("A", "República Checa", "Sudáfrica", "18 de junio de 2026"),
    ("A", "México", "Corea del Sur", "18 de junio de 2026"),
    ("A", "República Checa", "México", "24 de junio de 2026"),
    ("A", "Sudáfrica", "Corea del Sur", "24 de junio de 2026"),
    
    # Group B
    ("B", "Canadá", "Bosnia y Herzegovina", "12 de junio de 2026"),
    ("B", "Catar", "Suiza", "13 de junio de 2026"),
    ("B", "Suiza", "Bosnia y Herzegovina", "18 de junio de 2026"),
    ("B", "Canadá", "Catar", "18 de junio de 2026"),
    ("B", "Suiza", "Canadá", "24 de junio de 2026"),
    ("B", "Bosnia y Herzegovina", "Catar", "24 de junio de 2026"),
    
    # Group C
    ("C", "Brasil", "Marruecos", "13 de junio de 2026"),
    ("C", "Haití", "Escocia", "13 de junio de 2026"),
    ("C", "Brasil", "Haití", "19 de junio de 2026"),
    ("C", "Escocia", "Marruecos", "19 de junio de 2026"),
    ("C", "Escocia", "Brasil", "24 de junio de 2026"),
    ("C", "Marruecos", "Haití", "24 de junio de 2026"),
    
    # Group D
    ("D", "Estados Unidos", "Paraguay", "12 de junio de 2026"),
    ("D", "Australia", "Turquía", "13 de junio de 2026"),
    ("D", "Turquía", "Paraguay", "19 de junio de 2026"),
    ("D", "Estados Unidos", "Australia", "19 de junio de 2026"),
    ("D", "Turquía", "Estados Unidos", "25 de junio de 2026"),
    ("D", "Paraguay", "Australia", "25 de junio de 2026"),
    
    # Group E
    ("E", "Alemania", "Curazao", "14 de junio de 2026"),
    ("E", "Costa de Marfil", "Ecuador", "14 de junio de 2026"),
    ("E", "Alemania", "Costa de Marfil", "20 de junio de 2026"),
    ("E", "Ecuador", "Curazao", "20 de junio de 2026"),
    ("E", "Ecuador", "Alemania", "25 de junio de 2026"),
    ("E", "Curazao", "Costa de Marfil", "25 de junio de 2026"),
    
    # Group F
    ("F", "Países Bajos", "Japón", "14 de junio de 2026"),
    ("F", "Suecia", "Túnez", "14 de junio de 2026"),
    ("F", "Países Bajos", "Suecia", "20 de junio de 2026"),
    ("F", "Túnez", "Japón", "20 de junio de 2026"),
    ("F", "Japón", "Suecia", "25 de junio de 2026"),
    ("F", "Túnez", "Países Bajos", "25 de junio de 2026"),
    
    # Group G
    ("G", "Irán", "Nueva Zelanda", "15 de junio de 2026"),
    ("G", "Bélgica", "Egipto", "16 de junio de 2026"),
    ("G", "Bélgica", "Irán", "21 de junio de 2026"),
    ("G", "Nueva Zelanda", "Egipto", "21 de junio de 2026"),
    ("G", "Nueva Zelanda", "Bélgica", "26 de junio de 2026"),
    ("G", "Egipto", "Irán", "26 de junio de 2026"),
    
    # Group H
    ("H", "España", "Cabo Verde", "15 de junio de 2026"),
    ("H", "Arabia Saudita", "Uruguay", "15 de junio de 2026"),
    ("H", "España", "Arabia Saudita", "21 de junio de 2026"),
    ("H", "Uruguay", "Cabo Verde", "21 de junio de 2026"),
    ("H", "Uruguay", "España", "26 de junio de 2026"),
    ("H", "Cabo Verde", "Arabia Saudita", "26 de junio de 2026"),
    
    # Group I
    ("I", "Francia", "Senegal", "16 de junio de 2026"),
    ("I", "Irak", "Noruega", "16 de junio de 2026"),
    ("I", "Francia", "Irak", "22 de junio de 2026"),
    ("I", "Noruega", "Senegal", "22 de junio de 2026"),
    ("I", "Noruega", "Francia", "26 de junio de 2026"),
    ("I", "Senegal", "Irak", "26 de junio de 2026"),
    
    # Group J
    ("J", "Argentina", "Argelia", "16 de junio de 2026"),
    ("J", "Austria", "Jordania", "16 de junio de 2026"),
    ("J", "Argentina", "Austria", "22 de junio de 2026"),
    ("J", "Jordania", "Argelia", "22 de junio de 2026"),
    ("J", "Jordania", "Argentina", "27 de junio de 2026"),
    ("J", "Argelia", "Austria", "27 de junio de 2026"),
    
    # Group K
    ("K", "Portugal", "R. D. del Congo", "17 de junio de 2026"),
    ("K", "Uzbekistán", "Colombia", "17 de junio de 2026"),
    ("K", "Portugal", "Uzbekistán", "23 de junio de 2026"),
    ("K", "Colombia", "R. D. del Congo", "23 de junio de 2026"),
    ("K", "Colombia", "Portugal", "27 de junio de 2026"),
    ("K", "R. D. del Congo", "Uzbekistán", "27 de junio de 2026"),
    
    # Group L
    ("L", "Inglaterra", "Croacia", "17 de junio de 2026"),
    ("L", "Ghana", "Panamá", "17 de junio de 2026"),
    ("L", "Inglaterra", "Ghana", "23 de junio de 2026"),
    ("L", "Panamá", "Croacia", "23 de junio de 2026"),
    ("L", "Panamá", "Inglaterra", "27 de junio de 2026"),
    ("L", "Croacia", "Ghana", "27 de junio de 2026")
]

DEFAULT_PLAYERS = [
    "Carlos", "Sofía", "Alejandro", "Valeria", 
    "Mateo", "Camila", "Sebastián", "Daniela", 
    "Diego", "Mariana", "Nicolás", "Gabriela"
]

DATABASE_URL = os.environ.get("DATABASE_URL")
USING_POSTGRES = False
DB_INTEGRITY_ERRORS = (sqlite3.IntegrityError,)

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    try:
        import psycopg2
        import psycopg2.extras
        USING_POSTGRES = True
        DB_INTEGRITY_ERRORS = (psycopg2.IntegrityError,)
    except ImportError:
        pass

class HybridRow(dict):
    def __init__(self, data, tuple_data):
        super().__init__(data)
        self.tuple_data = tuple_data
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.tuple_data[key]
        return super().__getitem__(key)

class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, query, params=()):
        # Convert ? to %s for PostgreSQL query parameters
        query = query.replace('?', '%s')
        # Translate SQLite AUTOINCREMENT syntax to PostgreSQL SERIAL PRIMARY KEY
        if "INTEGER PRIMARY KEY AUTOINCREMENT" in query:
            query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        self.cursor.execute(query, params)
        
    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self._wrap_row(row)
        
    def fetchall(self):
        rows = self.cursor.fetchall()
        return [self._wrap_row(r) for r in rows]
        
    def _wrap_row(self, row):
        colnames = [desc[0] for desc in self.cursor.description]
        data = {col: row[i] for i, col in enumerate(colnames)}
        return HybridRow(data, row)
        
    def __getattr__(self, name):
        return getattr(self.cursor, name)

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        
    def cursor(self, *args, **kwargs):
        cursor = self.conn.cursor(*args, **kwargs)
        return PostgresCursorWrapper(cursor)
        
    def __getattr__(self, name):
        return getattr(self.conn, name)

def get_db_connection():
    if USING_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return PostgresConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

def init_db(reset=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if reset:
        cursor.execute("DROP TABLE IF EXISTS config")
        cursor.execute("DROP TABLE IF EXISTS group_matches")
        cursor.execute("DROP TABLE IF EXISTS matches")
        cursor.execute("DROP TABLE IF EXISTS assignments")
        cursor.execute("DROP TABLE IF EXISTS teams")
        cursor.execute("DROP TABLE IF EXISTS players")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        group_name TEXT NOT NULL,
        status TEXT DEFAULT 'Vivo',
        round_eliminated TEXT DEFAULT 'N/A'
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        player_id INTEGER,
        team_id INTEGER,
        PRIMARY KEY (player_id, team_id),
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_number INTEGER UNIQUE,
        round TEXT NOT NULL,
        team_a_id INTEGER,
        team_b_id INTEGER,
        winner_id INTEGER,
        FOREIGN KEY (team_a_id) REFERENCES teams(id),
        FOREIGN KEY (team_b_id) REFERENCES teams(id),
        FOREIGN KEY (winner_id) REFERENCES teams(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_number INTEGER UNIQUE,
        group_name TEXT NOT NULL,
        team_a_id INTEGER,
        team_b_id INTEGER,
        score_a INTEGER DEFAULT NULL,
        score_b INTEGER DEFAULT NULL,
        status TEXT DEFAULT 'Pendiente',
        match_date TEXT NOT NULL,
        FOREIGN KEY (team_a_id) REFERENCES teams(id),
        FOREIGN KEY (team_b_id) REFERENCES teams(id)
    )
    """)
    
    # Seed config defaults if empty
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("player_cost", "500"),
            ("pct_1st", "80"),
            ("pct_2nd", "20"),
            ("pct_3rd", "0")
        ]
        for k, v in defaults:
            cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (k, v))

    # Seed teams if empty
    cursor.execute("SELECT COUNT(*) FROM teams")
    if cursor.fetchone()[0] == 0:
        for t in DEFAULT_TEAMS:
            cursor.execute(
                "INSERT INTO teams (name, group_name, status, round_eliminated) VALUES (?, ?, 'Vivo', 'N/A')",
                (t["name"], t["group_name"])
            )
            
    # Seed players if empty
    cursor.execute("SELECT COUNT(*) FROM players")
    if cursor.fetchone()[0] == 0:
        for p in DEFAULT_PLAYERS:
            cursor.execute("INSERT INTO players (name) VALUES (?)", (p,))
            
    # Initialize matches if empty
    cursor.execute("SELECT COUNT(*) FROM matches")
    if cursor.fetchone()[0] == 0:
        initialize_matches(cursor)
        
    # Initialize group matches if empty
    cursor.execute("SELECT COUNT(*) FROM group_matches")
    if cursor.fetchone()[0] == 0:
        initialize_group_matches(cursor)
        
    conn.commit()
    conn.close()

def get_config(key, default_val=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return row["value"]
        return default_val
    except Exception:
        return default_val
    finally:
        conn.close()

def set_config(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM config WHERE key = ?", (key,))
        if cursor.fetchone():
            cursor.execute("UPDATE config SET value = ? WHERE key = ?", (str(value), key))
        else:
            cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error set_config: {e}")
        return False
    finally:
        conn.close()

def get_third_place_team():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get teams eliminated in Semifinales
        cursor.execute("SELECT id, name FROM teams WHERE round_eliminated = 'Semifinales'")
        losers = [dict(row) for row in cursor.fetchall()]
        if len(losers) < 2:
            return None
        
        # Calculate group stage standings to get their group stats
        standings = calculate_standings(cursor)
        loser_stats = []
        
        for loser in losers:
            found = False
            for g_name, g_teams in standings.items():
                for t_stats in g_teams:
                    if t_stats["id"] == loser["id"]:
                        loser_stats.append(t_stats)
                        found = True
                        break
                if found:
                    break
                    
        if len(loser_stats) < 2:
            return losers[0] if losers else None
            
        # Tiebreakers:
        # 1. points (pts) DESC
        # 2. goal difference (dif) DESC
        # 3. goals for (gf) DESC
        # 4. name ASC (alphabetical)
        loser_stats.sort(key=lambda x: (-x["pts"], -x["dif"], -x["gf"], x["name"]))
        return loser_stats[0]
    except Exception as e:
        print(f"Error get_third_place_team: {e}")
        return None
    finally:
        conn.close()

def initialize_matches(cursor):
    """
    Initializes the 31 matches of the perfect binary tree bracket (excluding group matches).
    All matches start with NULL values for teams and winners.
    """
    # Round of 32 (Dieciseisavos): Matches 1 to 16 (blank initially)
    for m_num in range(1, 17):
        cursor.execute(
            "INSERT INTO matches (match_number, round, team_a_id, team_b_id, winner_id) VALUES (?, 'Dieciseisavos', NULL, NULL, NULL)",
            (m_num,)
        )
        
    # Round of 16 (Octavos): Matches 17 to 24 (blank initially)
    for i in range(8):
        cursor.execute(
            "INSERT INTO matches (match_number, round, team_a_id, team_b_id, winner_id) VALUES (?, 'Octavos', NULL, NULL, NULL)",
            (i + 17,)
        )
        
    # Quarterfinals (Cuartos): Matches 25 to 28 (blank initially)
    for i in range(4):
        cursor.execute(
            "INSERT INTO matches (match_number, round, team_a_id, team_b_id, winner_id) VALUES (?, 'Cuartos', NULL, NULL, NULL)",
            (i + 25,)
        )
        
    # Semifinals (Semifinales): Matches 29 and 30 (blank initially)
    for i in range(2):
        cursor.execute(
            "INSERT INTO matches (match_number, round, team_a_id, team_b_id, winner_id) VALUES (?, 'Semifinales', NULL, NULL, NULL)",
            (i + 29,)
        )
        
    # Final: Match 31 (blank initially)
    cursor.execute(
        "INSERT INTO matches (match_number, round, team_a_id, team_b_id, winner_id) VALUES (31, 'Final', NULL, NULL, NULL)"
    )

def initialize_group_matches(cursor):
    """
    Seeds the direct duels of the group stage for the 48 teams (Groups A to L)
    using the official tournament dates (June 11 to June 27, 2026).
    """
    cursor.execute("SELECT id, name FROM teams")
    db_teams = {row["name"]: row["id"] for row in cursor.fetchall()}
    
    for match_num, (g_letter, t_a_name, t_b_name, m_date) in enumerate(GROUP_MATCHES_DEFS, 1):
        t_a_id = db_teams.get(t_a_name)
        t_b_id = db_teams.get(t_b_name)
        
        if not t_a_id or not t_b_id:
            continue
            
        cursor.execute("""
            INSERT INTO group_matches (match_number, group_name, team_a_id, team_b_id, score_a, score_b, status, match_date)
            VALUES (?, ?, ?, ?, NULL, NULL, 'Pendiente', ?)
        """, (match_num, g_letter, t_a_id, t_b_id, m_date))

# --- Group Standings and Calculations ---
def calculate_standings(cursor):
    """
    Computes standings for all 12 groups (A to L) in real-time based on group_matches.
    Returns a dict mapping group_name to a sorted list of dicts.
    """
    cursor.execute("SELECT id, name, group_name FROM teams")
    teams = [dict(row) for row in cursor.fetchall()]
    
    stats = {}
    for t in teams:
        stats[t["id"]] = {
            "id": t["id"],
            "name": t["name"],
            "group_name": t["group_name"],
            "pj": 0, "pg": 0, "pe": 0, "pp": 0,
            "gf": 0, "gc": 0, "dif": 0, "pts": 0
        }
        
    cursor.execute("""
        SELECT team_a_id, team_b_id, score_a, score_b 
        FROM group_matches 
        WHERE status = 'Jugado' AND score_a IS NOT NULL AND score_b IS NOT NULL
    """)
    matches = cursor.fetchall()
    
    for m in matches:
        ta = m["team_a_id"]
        tb = m["team_b_id"]
        sa = m["score_a"]
        sb = m["score_b"]
        
        stats[ta]["pj"] += 1
        stats[ta]["gf"] += sa
        stats[ta]["gc"] += sb
        stats[ta]["dif"] = stats[ta]["gf"] - stats[ta]["gc"]
        
        stats[tb]["pj"] += 1
        stats[tb]["gf"] += sb
        stats[tb]["gc"] += sa
        stats[tb]["dif"] = stats[tb]["gf"] - stats[tb]["gc"]
        
        if sa > sb:
            stats[ta]["pg"] += 1
            stats[ta]["pts"] += 3
            stats[tb]["pp"] += 1
        elif sb > sa:
            stats[tb]["pg"] += 1
            stats[tb]["pts"] += 3
            stats[ta]["pp"] += 1
        else:
            stats[ta]["pe"] += 1
            stats[ta]["pts"] += 1
            stats[tb]["pe"] += 1
            stats[tb]["pts"] += 1
            
    groups = {}
    for t_id, t_stats in stats.items():
        g = t_stats["group_name"]
        if g not in groups:
            groups[g] = []
        groups[g].append(t_stats)
        
    for g in groups:
        groups[g].sort(key=lambda x: (-x["pts"], -x["dif"], -x["gf"], x["name"]))
        
    return groups

def get_best_third_places(group_standings):
    """
    Takes the group standings dict, extracts the 3rd-place team from each of the 12 groups,
    ranks them, and returns the top 8.
    """
    third_places = []
    for g_name, standings in group_standings.items():
        if len(standings) >= 3:
            third_places.append(standings[2])
            
    third_places.sort(key=lambda x: (-x["pts"], -x["dif"], -x["gf"], x["name"]))
    return third_places[:8]

def get_group_matches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gm.id, gm.match_number, gm.group_name, gm.score_a, gm.score_b, gm.status, gm.match_date,
               gm.team_a_id, t_a.name as team_a_name, t_a.status as team_a_status,
               gm.team_b_id, t_b.name as team_b_name, t_b.status as team_b_status
        FROM group_matches gm
        JOIN teams t_a ON gm.team_a_id = t_a.id
        JOIN teams t_b ON gm.team_b_id = t_b.id
        ORDER BY gm.match_number
    """)
    matches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return matches

def propagate_match_change(cursor, match_number):
    """
    Recursively propagates changes down the bracket tree.
    """
    cursor.execute("SELECT winner_id FROM matches WHERE match_number = ?", (match_number,))
    match = cursor.fetchone()
    winner_id = match["winner_id"] if match else None
    
    next_match_num = None
    slot = 'A'
    
    if match_number in MATCH_PROPAGATION:
        next_match_num, slot = MATCH_PROPAGATION[match_number]
        
    if next_match_num:
        cursor.execute("SELECT team_a_id, team_b_id, winner_id FROM matches WHERE match_number = ?", (next_match_num,))
        next_match = cursor.fetchone()
        
        curr_val = next_match["team_a_id"] if slot == 'A' else next_match["team_b_id"]
        
        if curr_val != winner_id:
            if slot == 'A':
                cursor.execute("UPDATE matches SET team_a_id = ?, winner_id = NULL WHERE match_number = ?", (winner_id, next_match_num))
            else:
                cursor.execute("UPDATE matches SET team_b_id = ?, winner_id = NULL WHERE match_number = ?", (winner_id, next_match_num))
                
            propagate_match_change(cursor, next_match_num)

def recalculate_team_statuses(cursor):
    """
    Recalculates the status of all teams in the tournament (Vivo, Eliminado, Campeón, Subcampeón)
    based on the current results of all played group matches and bracket matches.
    """
    # 1. Reset all teams to Vivo
    cursor.execute("UPDATE teams SET status = 'Vivo', round_eliminated = 'N/A'")
    
    # 2. Get standings to check group-stage eliminations
    standings = calculate_standings(cursor)
    
    # Check group completeness
    cursor.execute("""
        SELECT group_name, COUNT(*) as total, SUM(CASE WHEN status = 'Jugado' THEN 1 ELSE 0 END) as played
        FROM group_matches
        GROUP BY group_name
    """)
    completeness = {row["group_name"]: (row["played"] == row["total"]) for row in cursor.fetchall()}
    
    # Check if all group matches are played to rank third places
    cursor.execute("SELECT COUNT(*) FROM group_matches WHERE status = 'Jugado'")
    completed_group_matches = cursor.fetchone()[0]
    is_group_stage_complete = (completed_group_matches == 72)
    
    best_thirds_ids = set()
    if is_group_stage_complete:
        best_thirds = get_best_third_places(standings)
        best_thirds_ids = {bt["id"] for bt in best_thirds}
        
    # Mark group-stage eliminations
    for g_name, g_teams in standings.items():
        if completeness.get(g_name, False):
            # 4th place (index 3) is ALWAYS eliminated from group stage
            if len(g_teams) >= 4:
                t4_id = g_teams[3]["id"]
                cursor.execute("UPDATE teams SET status = 'Eliminado', round_eliminated = 'Fase de Grupos' WHERE id = ?", (t4_id,))
                
            # 3rd place (index 2) is eliminated if the entire group stage is complete and they are not in the top 8 best thirds
            if len(g_teams) >= 3:
                t3_id = g_teams[2]["id"]
                if is_group_stage_complete and t3_id not in best_thirds_ids:
                    cursor.execute("UPDATE teams SET status = 'Eliminado', round_eliminated = 'Fase de Grupos' WHERE id = ?", (t3_id,))
                    
    # 3. Process bracket matches in order of match_number to determine knockout eliminations
    cursor.execute("SELECT match_number, round, team_a_id, team_b_id, winner_id FROM matches ORDER BY match_number")
    matches = cursor.fetchall()
    
    for m in matches:
        winner_id = m["winner_id"]
        team_a_id = m["team_a_id"]
        team_b_id = m["team_b_id"]
        round_name = m["round"]
        
        if winner_id:
            loser_id = team_b_id if winner_id == team_a_id else team_a_id
            if loser_id:
                cursor.execute("UPDATE teams SET status = 'Eliminado', round_eliminated = ? WHERE id = ?", (round_name, loser_id))
            
            if m["match_number"] == 31:
                cursor.execute("UPDATE teams SET status = 'Campeón', round_eliminated = 'N/A' WHERE id = ?", (winner_id,))
                if loser_id:
                    cursor.execute("UPDATE teams SET status = 'Subcampeón', round_eliminated = 'N/A' WHERE id = ?", (loser_id,))

def update_bracket_from_groups(cursor):
    """
    Computes Winner (1st) and Runner-up (2nd) for each of the 12 groups (A to L)
    and seeds them into Matches 1-16 of the Round of 32.
    Also, once all 72 group stage matches are played, dynamically seeds the 8 best
    third-place teams.
    """
    standings = calculate_standings(cursor)
    
    # Check group completeness
    cursor.execute("""
        SELECT group_name, COUNT(*) as total, SUM(CASE WHEN status = 'Jugado' THEN 1 ELSE 0 END) as played
        FROM group_matches
        GROUP BY group_name
    """)
    completeness = {row["group_name"]: (row["played"] == row["total"]) for row in cursor.fetchall()}
    
    group_winners = {}
    group_runners = {}
    
    for g in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]:
        if completeness.get(g, False) and len(standings.get(g, [])) >= 2:
            group_winners[g] = standings[g][0]["id"]
            group_runners[g] = standings[g][1]["id"]
        else:
            group_winners[g] = None
            group_runners[g] = None
            
    # Check if group stage is fully completed in database
    cursor.execute("SELECT COUNT(*) FROM group_matches WHERE status = 'Jugado'")
    completed_count = cursor.fetchone()[0]
    is_group_stage_complete = (completed_count == 72)
    
    third_places_ids = [None] * 8
    if is_group_stage_complete:
        best_thirds = get_best_third_places(standings)
        for i, bt in enumerate(best_thirds):
            third_places_ids[i] = bt["id"]
            
    # Seeding updates for Matches 1 to 16
    match_updates = {
        1: (group_runners.get('A'), group_runners.get('B')),
        2: (group_winners.get('E'), third_places_ids[0]),
        3: (group_winners.get('F'), group_runners.get('C')),
        4: (group_winners.get('C'), group_runners.get('F')),
        5: (group_winners.get('I'), third_places_ids[1]),
        6: (group_runners.get('E'), group_runners.get('I')),
        7: (group_winners.get('A'), third_places_ids[2]),
        8: (group_winners.get('L'), third_places_ids[3]),
        9: (group_winners.get('G'), third_places_ids[4]),
        10: (group_winners.get('D'), third_places_ids[5]),
        11: (group_winners.get('H'), group_runners.get('J')),
        12: (group_runners.get('K'), group_runners.get('L')),
        13: (group_winners.get('B'), third_places_ids[6]),
        14: (group_runners.get('D'), group_runners.get('G')),
        15: (group_winners.get('J'), group_runners.get('H')),
        16: (group_winners.get('K'), third_places_ids[7])
    }
    
    for m_num, (new_a, new_b) in match_updates.items():
        cursor.execute("SELECT team_a_id, team_b_id FROM matches WHERE match_number = ?", (m_num,))
        m_curr = cursor.fetchone()
        
        curr_a = m_curr["team_a_id"] if m_curr else None
        curr_b = m_curr["team_b_id"] if m_curr else None
        
        if new_a is not None and curr_a != new_a:
            cursor.execute("UPDATE matches SET team_a_id = ?, winner_id = NULL WHERE match_number = ?", (new_a, m_num))
            propagate_match_change(cursor, m_num)
        elif new_a is None and curr_a is not None:
            cursor.execute("UPDATE matches SET team_a_id = NULL, winner_id = NULL WHERE match_number = ?", (m_num,))
            propagate_match_change(cursor, m_num)
            
        if new_b is not None and curr_b != new_b:
            cursor.execute("UPDATE matches SET team_b_id = ?, winner_id = NULL WHERE match_number = ?", (new_b, m_num))
            propagate_match_change(cursor, m_num)
        elif new_b is None and curr_b is not None:
            cursor.execute("UPDATE matches SET team_b_id = NULL, winner_id = NULL WHERE match_number = ?", (m_num,))
            propagate_match_change(cursor, m_num)

def update_group_match_score(match_id, score_a, score_b):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE group_matches SET score_a = ?, score_b = ?, status = 'Jugado' WHERE id = ?",
        (score_a, score_b, match_id)
    )
    
    update_bracket_from_groups(cursor)
    recalculate_team_statuses(cursor)
    
    conn.commit()
    conn.close()
    return True, "Marcador de fase de grupos actualizado correctamente."

# --- Players Management ---
def get_players():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players ORDER BY name")
    players = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return players

def add_player(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name.strip(),))
        conn.commit()
        success = True
    except DB_INTEGRITY_ERRORS:
        success = False
    conn.close()
    return success

def delete_player(player_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    cursor.execute("DELETE FROM assignments WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()

# --- Teams Management ---
def get_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY group_name, name")
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams

def update_team_status(team_id, status, round_eliminated='N/A'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE teams SET status = ?, round_eliminated = ? WHERE id = ?",
        (status, round_eliminated, team_id)
    )
    conn.commit()
    conn.close()

# --- Draft / Assignments Management ---
def get_assignments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id as player_id, p.name as player_name, 
               t1.id as team1_id, t1.name as team1_name, t1.status as team1_status, t1.group_name as team1_group, t1.round_eliminated as team1_elim,
               t2.id as team2_id, t2.name as team2_name, t2.status as team2_status, t2.group_name as team2_group, t2.round_eliminated as team2_elim
        FROM players p
        LEFT JOIN (
            SELECT a.player_id, t.*, ROW_NUMBER() OVER(PARTITION BY a.player_id ORDER BY t.id) as rn
            FROM assignments a
            JOIN teams t ON a.team_id = t.id
        ) t1 ON p.id = t1.player_id AND t1.rn = 1
        LEFT JOIN (
            SELECT a.player_id, t.*, ROW_NUMBER() OVER(PARTITION BY a.player_id ORDER BY t.id) as rn
            FROM assignments a
            JOIN teams t ON a.team_id = t.id
        ) t2 ON p.id = t2.player_id AND t2.rn = 2
    """)
    assignments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assignments

def clear_assignments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments")
    conn.commit()
    conn.close()

FIFA_WORLD_RANKINGS = [
    "Francia", "España", "Argentina", "Inglaterra", "Portugal", "Brasil",
    "Países Bajos", "Marruecos", "Bélgica", "Alemania", "Croacia", "Italia",
    "Colombia", "Senegal", "México", "Estados Unidos", "Uruguay", "Japón",
    "Suiza", "Dinamarca", "Irán", "Turquía", "Ecuador", "Austria",
    "Corea del Sur", "Australia", "Argelia", "Egipto", "Canadá",
    "Ucrania", "Polonia", "Suecia", "Gales", "Hungría", "Perú", "Chile",
    "Costa de Marfil", "Túnez", "Noruega", "Paraguay", "República Checa",
    "Escocia", "Arabia Saudita", "Irak", "Uzbekistán", "Bosnia y Herzegovina",
    "Cabo Verde", "Ghana", "Catar", "Panamá", "Sudáfrica", "R. D. del Congo",
    "Haití", "Curazao", "Jordania", "Nueva Zelanda"
]

def get_top_24_qualified_teams(available_team_names):
    qualified = []
    for team in FIFA_WORLD_RANKINGS:
        if team in available_team_names:
            qualified.append(team)
    for team in available_team_names:
        if team not in qualified:
            qualified.append(team)
    return qualified[:24]

TOP_24_FIFA_TEAMS = get_top_24_qualified_teams([t["name"] for t in DEFAULT_TEAMS])

def make_random_draft():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM players")
    players = [row["id"] for row in cursor.fetchall()]
    
    # Query all team names dynamically from the database
    cursor.execute("SELECT id, name FROM teams")
    db_teams = cursor.fetchall()
    db_team_names = [row["name"] for row in db_teams]
    team_name_to_id = {row["name"]: row["id"] for row in db_teams}
    
    # Compute the top 24 qualified teams dynamically (ordered by FIFA rank)
    top_24_names = get_top_24_qualified_teams(db_team_names)
    
    if len(players) != 12:
        conn.close()
        return False, "Se requieren exactamente 12 jugadores registrados para realizar el sorteo."
        
    if len(top_24_names) != 24:
        conn.close()
        return False, f"Se requieren exactamente 24 selecciones en el pool de sorteo (actualmente hay {len(top_24_names)})."
        
    # Separate into Bombo 1 (Top 12 Cabezas de Serie) and Bombo 2 (Ranks 13-24)
    bombo1_names = top_24_names[:12]
    bombo2_names = top_24_names[12:24]
    
    bombo1_ids = [team_name_to_id[name] for name in bombo1_names]
    bombo2_ids = [team_name_to_id[name] for name in bombo2_names]
    
    cursor.execute("DELETE FROM assignments")
    
    random.shuffle(bombo1_ids)
    random.shuffle(bombo2_ids)
    
    for i, p_id in enumerate(players):
        t1 = bombo1_ids[i]
        t2 = bombo2_ids[i]
        cursor.execute("INSERT INTO assignments (player_id, team_id) VALUES (?, ?)", (p_id, t1))
        cursor.execute("INSERT INTO assignments (player_id, team_id) VALUES (?, ?)", (p_id, t2))
        
    conn.commit()
    conn.close()
    return True, "Sorteo completado con éxito."


def assign_teams_manually(player_assignments):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments")
    
    for pa in player_assignments:
        for t_id in pa['team_ids']:
            cursor.execute("INSERT INTO assignments (player_id, team_id) VALUES (?, ?)", (pa['player_id'], t_id))
            
    conn.commit()
    conn.close()

# --- Bracket & Matches Management ---
def get_matches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.match_number, m.round, 
               m.team_a_id, t_a.name as team_a_name, t_a.status as team_a_status,
               m.team_b_id, t_b.name as team_b_name, t_b.status as team_b_status,
               m.winner_id, t_w.name as winner_name
        FROM matches m
        LEFT JOIN teams t_a ON m.team_a_id = t_a.id
        LEFT JOIN teams t_b ON m.team_b_id = t_b.id
        LEFT JOIN teams t_w ON m.winner_id = t_w.id
        ORDER BY m.match_number
    """)
    matches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return matches

def eliminate_in_group_stage(team_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE teams SET status = 'Eliminado', round_eliminated = 'Fase de Grupos' WHERE id = ?", (team_id,))
    cursor.execute("SELECT * FROM matches WHERE (team_a_id = ? OR team_b_id = ?) AND winner_id IS NULL", (team_id, team_id))
    matches_to_resolve = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    for m in matches_to_resolve:
        m_num = m["match_number"]
        t_a = m["team_a_id"]
        t_b = m["team_b_id"]
        
        survivor_id = t_b if t_a == team_id else t_a
        
        if survivor_id:
            update_match_winner(m_num, survivor_id)
            
    return True, "Equipo eliminado en Fase de Grupos. El oponente avanza en el bracket de forma automática."

def update_match_winner(match_number, winner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM matches WHERE match_number = ?", (match_number,))
    match = cursor.fetchone()
    if not match:
        conn.close()
        return False, "Partido no encontrado."
        
    team_a_id = match["team_a_id"]
    team_b_id = match["team_b_id"]
    
    if winner_id not in [team_a_id, team_b_id]:
        conn.close()
        return False, "El ganador debe ser uno de los dos equipos participantes."
        
    cursor.execute("UPDATE matches SET winner_id = ? WHERE match_number = ?", (winner_id, match_number))
    
    propagate_match_change(cursor, match_number)
    recalculate_team_statuses(cursor)
    
    conn.commit()
    conn.close()
    return True, "Ganador registrado y árbol de eliminatorias actualizado correctamente."

def reset_tournament_brackets():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE teams SET status = 'Vivo', round_eliminated = 'N/A'")
    cursor.execute("DELETE FROM matches")
    initialize_matches(cursor)
    cursor.execute("UPDATE group_matches SET score_a = NULL, score_b = NULL, status = 'Pendiente'")
    
    conn.commit()
    conn.close()
    return True, "Torneo reiniciado. Todos los equipos vuelven a estar Vivos y el bracket se ha restablecido."
