import os
import mysql.connector

def create_connection():
    """
    Creating a connection to the 'fantasyfootballdb' database.
    Connection settings come from environment variables (defaults shown):
        FF_DB_USER=root, FF_DB_PASSWORD='', FF_DB_HOST=127.0.0.1, FF_DB_NAME=fantasyfootballdb
    :return: Connection object
    """
    try:
        conn = mysql.connector.connect(
            user=os.environ.get('FF_DB_USER', 'root'),
            password=os.environ.get('FF_DB_PASSWORD', ''),
            host=os.environ.get('FF_DB_HOST', '127.0.0.1'),
            database=os.environ.get('FF_DB_NAME', 'fantasyfootballdb')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Query A: My Team's Performance for a given week
def query_a_my_teams_performance(conn, week):
    """
    Query A: Performance for my team for a given week
    :param conn: Connection object
    :return: Nothing
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.TeamName, 
               p.Name, 
               p.Position, 
               rs.StatusName AS LineupStatus, 
               s.Week, 
               s.FantasyPoints
        FROM Fantasy_Teams f
        JOIN Roster r ON f.FantasyTeamID = r.FantasyTeamID
        JOIN NFL_Players p ON r.PlayerID = p.PlayerID
        JOIN Roster_Status rs ON r.StatusID = rs.StatusID
        JOIN Player_Stats s ON p.PlayerID = s.PlayerID
        WHERE f.ManagerName = 'Jesse' 
          AND s.Week = %s
        ORDER BY s.FantasyPoints DESC
    """,(week,))

    rows = cursor.fetchall()

    print(f"\nQuery A: My Team Performance in Week {week}")
    print("TeamName | PlayerName | Position | LineupStatus | Week | FantasyPoints")
    print("-" * 70)
    
    """
    Currently, my Query A shows the fantasy points for each player. 
    However, a very important metric in fantasy football is the total fantasy points scored from all starters on my team.
    I calculated 3 summation outputs:
        1. Summation of my total starter's fantasy points (actual fantasy points my team scored that week).
        2. Summation of my bench's points.
        3. Max points that I could've scored that week if I had started the best possible lineup. 
            (1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX (RB/WR/TE) / 1 K / 1 DEF)
    """

    starter_points = 0
    bench_points = 0
    players_by_position = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'K': [], 'DEF': []}

    for row in rows:
        fantasy_points = row[5]
        position = row[2]
        status = row[3]
        
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {fantasy_points:.2f}")
        
        # Summing the total points scored by Starters and Bench players
        if status == 'Starter':
            starter_points += fantasy_points
        elif status == 'Bench':
            bench_points += fantasy_points
        
        # Summing the total points scored by each position group
        if position in players_by_position:
            players_by_position[position].append(fantasy_points)

    max_points = 0
    
    # 1 QB
    if players_by_position['QB']:
        max_points += max(players_by_position['QB'])
    
    # 2 RB
    if len(players_by_position['RB']) >= 2:
        max_points += sum(sorted(players_by_position['RB'], reverse=True)[:2]) # reverse=True for DESC order
    elif players_by_position['RB']:
        max_points += max(players_by_position['RB'])
    
    # 2 WR
    if len(players_by_position['WR']) >= 2:
        max_points += sum(sorted(players_by_position['WR'], reverse=True)[:2]) # reverse=True for DESC order
    elif players_by_position['WR']:
        max_points += max(players_by_position['WR'])
    
    # 1 TE
    if players_by_position['TE']:
        max_points += max(players_by_position['TE'])
    
    # 1 K
    if players_by_position['K']:
        max_points += max(players_by_position['K'])
    
    # 1 DEF 
    if players_by_position['DEF']:
        max_points += max(players_by_position['DEF'])
    
    # 1 FLEX -- picking the highest-scoring RB, WR, or TE not already used
    flex_candidates = []
    for pos in ['RB', 'WR', 'TE']:
        # Exclude top 2 RBs, top 2 WRs, and top TE if already used
        if pos == 'RB' and len(players_by_position['RB']) > 2:
            flex_candidates.extend(sorted(players_by_position['RB'], reverse=True)[2:]) # reverse=True for DESC order
        elif pos == 'RB' and len(players_by_position['RB']) == 2:
            continue  # No RBs left to fill spots
        elif pos == 'RB' and len(players_by_position['RB']) == 1:
            flex_candidates.extend(players_by_position['RB'])
        elif pos == 'WR' and len(players_by_position['WR']) > 2:
            flex_candidates.extend(sorted(players_by_position['WR'], reverse=True)[2:]) # reverse=True for DESC order 
        elif pos == 'WR' and len(players_by_position['WR']) == 2:
            continue  # No WRs left to fill spots
        elif pos == 'WR' and len(players_by_position['WR']) == 1:
            flex_candidates.extend(players_by_position['WR'])
        elif pos == 'TE' and len(players_by_position['TE']) > 1:
            flex_candidates.extend(sorted(players_by_position['TE'], reverse=True)[1:])
        elif pos == 'TE' and len(players_by_position['TE']) == 1:
            continue  # Top TE already used
    
    if flex_candidates:
        max_points += max(flex_candidates)

    print(f"\nTotal Starters' Fantasy Points: {starter_points:.2f}")
    print(f"Total Bench Fantasy Points: {bench_points:.2f}")
    print(f"Maximum Possible Fantasy Points: {max_points:.2f}")
    
    cursor.close()

# Query C: Comparing WRs on my Roster vs. Waiver Wire
def query_c_wr_comparison(conn, week_1, week_2):
    """
    Query C: Comparing WRs on my roster vs. waiver wire for a range of weeks
    :param conn: Connection object
    :return: Nothing
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 'My Roster' AS Source, 
               p.Name, 
               AVG(s.FantasyPoints) AS AvgLastWeeks
        FROM Fantasy_Teams f
        JOIN Roster r ON f.FantasyTeamID = r.FantasyTeamID
        JOIN NFL_Players p ON r.PlayerID = p.PlayerID
        JOIN Player_Stats s ON p.PlayerID = s.PlayerID
        WHERE f.ManagerName = 'Jesse' 
          AND p.Position = 'WR' 
          AND s.Week BETWEEN %s AND %s
        GROUP BY p.Name
        UNION
        SELECT 'Waiver Wire' AS Source, 
               p.Name, 
               AVG(s.FantasyPoints) AS AvgLastWeeks
        FROM NFL_Players p
        JOIN Player_Stats s ON p.PlayerID = s.PlayerID
        JOIN Player_Status ps ON p.StatusID = ps.StatusID
        WHERE p.Position = 'WR' 
          AND ps.StatusName = 'Waiver' 
          AND s.Week BETWEEN %s AND %s
        GROUP BY p.Name
        ORDER BY AvgLastWeeks DESC
        LIMIT 30 -- added a limit here because the print out was extremely long
    """,(week_1, week_2, week_1, week_2))
    rows = cursor.fetchall()
    
    print(f"\nQuery C: WRs - My Roster vs. Waiver Wire (Weeks {week_1}-{week_2})")
    print("Source | PlayerName | AvgLastWeeks")
    print("-" * 50)
    
    # Calculating average points for roster
    roster_total = 0
    roster_count = 0
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]:.2f}")
        if row[0] == 'My Roster':
            roster_total += row[2]
            roster_count += 1
    
    # Print averages
    if roster_count > 0:
        print(f"\nAverage Points for My Roster: {roster_total / roster_count:.2f}")
    
    cursor.close()

# Query D: Add and Remove a player from my Roster
def query_d_add_player_to_my_roster(conn, player_id):
    """
    Add and remove player from my roster
    :param conn: Connection object
    :return: Nothing
    """
    cursor = conn.cursor()
    
    # Displaying my initial roster
    cursor.execute("""
        SELECT p.Name, p.Position, rs.StatusName
        FROM Roster r
        JOIN NFL_Players p ON r.PlayerID = p.PlayerID
        JOIN Roster_Status rs ON r.StatusID = rs.StatusID
        JOIN Fantasy_Teams f ON r.FantasyTeamID = f.FantasyTeamID
        WHERE f.ManagerName = 'Jesse'
    """)
    rows = cursor.fetchall()
    print("\nQuery D: Initial Roster")
    print("PlayerName | Position | Status")
    print("-" * 40)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]}")
    
    # Adding a player to my roster
    try:
        cursor.execute("""
            INSERT INTO Roster (FantasyTeamID, PlayerID, StatusID)
            VALUES (
                (SELECT FantasyTeamID FROM Fantasy_Teams WHERE ManagerName = 'Jesse'),
                %s,
                (SELECT StatusID FROM Roster_Status WHERE StatusName = 'Bench')
            )
        """, (player_id,))
        conn.commit()
        print(f"\nPlayer {player_id} added to roster.")
        
        # Updating the player status to Rostered
        cursor.execute("""
            UPDATE NFL_Players
            SET StatusID = (SELECT StatusID FROM Player_Status WHERE StatusName = 'Rostered')
            WHERE PlayerID = %s
        """, (player_id,))
        conn.commit()
        print(f"Player {player_id} status updated to Rostered.")
        
        # Show updated roster
        cursor.execute("""
            SELECT p.Name, p.Position, rs.StatusName
            FROM Roster r
            JOIN NFL_Players p ON r.PlayerID = p.PlayerID
            JOIN Roster_Status rs ON r.StatusID = rs.StatusID
            JOIN Fantasy_Teams f ON r.FantasyTeamID = f.FantasyTeamID
            WHERE f.ManagerName = 'Jesse'
        """)
        rows = cursor.fetchall()
        print("\nUpdated Roster")
        print("PlayerName | Position | Status")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")

        ######
        # Leaving the Undo Section in here. For the change to actually be implimented, I will remove all excuted commands below here:
        #####

        cursor.execute("""
            DELETE FROM Roster
            WHERE PlayerID = %s
              AND FantasyTeamID = (SELECT FantasyTeamID FROM Fantasy_Teams WHERE ManagerName = 'Jesse')
        """, (player_id,))
        conn.commit()
        print(f"\nPlayer {player_id} removed from roster.")
        
        cursor.execute("""
            UPDATE NFL_Players
            SET StatusID = (SELECT StatusID FROM Player_Status WHERE StatusName = 'Waiver')
            WHERE PlayerID = %s
        """,(player_id,))
        conn.commit()
        print(f"Player {player_id} status reverted to Waiver.")
        
        # Show final roster
        cursor.execute("""
            SELECT p.Name, p.Position, rs.StatusName
            FROM Roster r
            JOIN NFL_Players p ON r.PlayerID = p.PlayerID
            JOIN Roster_Status rs ON r.StatusID = rs.StatusID
            JOIN Fantasy_Teams f ON r.FantasyTeamID = f.FantasyTeamID
            WHERE f.ManagerName = 'Jesse'
        """)
        rows = cursor.fetchall()
        print("\nFinal Roster")
        print("PlayerName | Position | Status")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")
    
    except mysql.connector.Error as err:
        print(f"Error in roster management: {err}")
        conn.rollback()
    
    cursor.close()

# Query H: Top # of Players this season from any position 
def query_h_top_players_by_position(conn, position, limit):
    """
    Query H: Displaying the top # of players from any postion by ordered by total fantasy points this season
    :param conn: Connection object
    :return: Nothing
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.Name, 
            p.Position, 
            SUM(s.FantasyPoints) AS TotalPoints
        FROM NFL_Players p
        JOIN Player_Stats s ON p.PlayerID = s.PlayerID
        WHERE p.Position = %s
        GROUP BY p.PlayerID, p.Name, p.Position
        ORDER BY TotalPoints DESC
        LIMIT %s;
    """, (position, limit))
    
    rows = cursor.fetchall()
    print(f"\nQuery H: Top {limit} {position}s by Total Fantasy Points")
    print("Rank | PlayerName | TotalPoints")
    print("-" * 40)
    for i, row in enumerate(rows, 1):
        print(f"{i} | {row[0]} | {row[2]:.2f}")
    cursor.close()

if __name__ == '__main__':
    conn = create_connection()
    if conn is None:
        exit()
    
    # edit/run queries here
    query_a_my_teams_performance(conn, 5)
    query_c_wr_comparison(conn, 1, 5)
    query_d_add_player_to_my_roster(conn, 500)
    query_h_top_players_by_position(conn, 'QB', 5)
    
    conn.close()