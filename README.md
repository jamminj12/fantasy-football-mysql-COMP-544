# Fantasy Football League Database (MySQL + Python)

A MySQL database for one fantasy football league: teams, rosters, weekly player scoring, waiver-wire status, injuries and add/drop transactions. It includes sample data from a real 12-team league (2025 season, Weeks 1-5), ten example queries and a small Python script that runs four of them.

Semester project for a graduate database systems course (COMP 544, Grove City College, Fall 2025).

## Schema

Ten tables: four main tables, one stats table and four lookup tables. Status values live in lookup tables instead of `ENUM`s, so foreign keys keep them consistent.

```mermaid
erDiagram
    Fantasy_Teams ||--o{ Roster : "has"
    NFL_Players   ||--o| Roster : "is on (at most one team)"
    Roster_Status ||--o{ Roster : "Starter / Bench / IR"
    Player_Status ||--o{ NFL_Players : "Rostered / Waiver"
    NFL_Players   ||--o{ Player_Stats : "weekly points"
    NFL_Players   ||--o{ Injuries : "reports"
    Injury_Status ||--o{ Injuries : "O / Q / D / SUSP ..."
    Fantasy_Teams ||--o{ Transactions : "makes"
    NFL_Players   ||--o{ Transactions : "involves"
    Transaction_Type ||--o{ Transactions : "Add / Drop / Trade"

    Fantasy_Teams {
        int FantasyTeamID PK
        varchar TeamName
        varchar ManagerName
    }
    NFL_Players {
        int PlayerID PK
        varchar Name
        varchar Position
        char NFLTeam
        int StatusID FK
    }
    Roster {
        int RosterID PK
        int FantasyTeamID FK
        int PlayerID FK "UNIQUE"
        int StatusID FK
    }
    Player_Stats {
        int StatID PK
        int PlayerID FK
        int Week
        decimal FantasyPoints
    }
    Transactions {
        int TransactionID PK
        int FantasyTeamID FK
        int PlayerID FK
        int TransactionTypeID FK
        datetime Date
    }
    Injuries {
        int InjuryID PK
        int PlayerID FK
        int InjuryStatusID FK
        varchar InjuryType
    }
    Player_Status {
        int StatusID PK
        varchar StatusName
    }
    Roster_Status {
        int StatusID PK
        varchar StatusName
    }
    Transaction_Type {
        int TransactionTypeID PK
        varchar TypeName
    }
    Injury_Status {
        int InjuryStatusID PK
        varchar StatusCode
    }
```

## Running it

Needs MySQL 8.0+.

```bash
mysql -u root -p < sql/01_create_schema.sql     # creates FantasyFootballDB and all tables
mysql -u root -p < sql/02_insert_data.sql       # loads the sample league
mysql -u root -p < sql/03_example_queries.sql   # runs queries a-j
```

For the Python script, run `pip install -r python/requirements.txt`, then `python python/ff_queries.py`. It connects as `root` on localhost by default. Override with the `FF_DB_USER`, `FF_DB_PASSWORD`, `FF_DB_HOST` and `FF_DB_NAME` environment variables.

## Notes

- Sample data comes from a Yahoo fantasy league export and FantasyPros weekly scoring. The other eleven managers' names are replaced with placeholders. It's third-party data, included for demonstration only.
- Known bug: `ff_queries.py` looks for position `'DEF'`, but the data uses `'DST'`, so defenses are left out of the "maximum possible points" calculation.
