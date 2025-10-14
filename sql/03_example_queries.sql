-- Example queries (a-j) for FantasyFootballDB.
-- Written against the Week 1-5 sample data in 02_insert_data.sql.
-- Requires MySQL 8.0+ (query i uses a window function).
-- 'Jesse' is the manager whose team is treated as "my team".

USE FantasyFootballDB;

-- query a
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
  AND s.Week = 4
ORDER BY s.FantasyPoints DESC;


-- query b
SELECT p.Position, 
       p.Name, 
       s.FantasyPoints, 
       rs.StatusName AS LineupStatus
FROM Roster r
JOIN NFL_Players p ON r.PlayerID = p.PlayerID
JOIN Roster_Status rs ON r.StatusID = rs.StatusID
JOIN Player_Stats s ON p.PlayerID = s.PlayerID
JOIN Fantasy_Teams f ON r.FantasyTeamID = f.FantasyTeamID
WHERE f.ManagerName = 'Jesse' 
  AND s.Week = 2
ORDER BY p.Position, s.FantasyPoints DESC;


-- query c
-- My WRs
SELECT 'My Roster' AS Source, 
       p.Name, 
       AVG(s.FantasyPoints) AS AvgLast4Weeks
FROM Fantasy_Teams f
JOIN Roster r ON f.FantasyTeamID = r.FantasyTeamID
JOIN NFL_Players p ON r.PlayerID = p.PlayerID
JOIN Player_Stats s ON p.PlayerID = s.PlayerID
WHERE f.ManagerName = 'Jesse' 
  AND p.Position = 'WR' 
  AND s.Week BETWEEN 2 AND 5
GROUP BY p.Name
UNION
-- Waiver Wire WRs
SELECT 'Waiver Wire' AS Source, 
       p.Name, 
       AVG(s.FantasyPoints) AS AvgLast4Weeks
FROM NFL_Players p
JOIN Player_Stats s ON p.PlayerID = s.PlayerID
JOIN Player_Status ps ON p.StatusID = ps.StatusID
WHERE p.Position = 'WR' 
  AND ps.StatusName = 'Waiver' 
  AND s.Week BETWEEN 2 AND 5
GROUP BY p.Name
ORDER BY AvgLast4Weeks DESC;


-- query d
-- Add player to roster
INSERT INTO Roster (FantasyTeamID, PlayerID, StatusID)
VALUES (
    (SELECT FantasyTeamID FROM Fantasy_Teams WHERE ManagerName = 'Jesse'),
    500,
    (SELECT StatusID FROM Roster_Status WHERE StatusName = 'Bench')
);
-- Update player status to Rostered
UPDATE NFL_Players
SET StatusID = (SELECT StatusID FROM Player_Status WHERE StatusName = 'Rostered')
WHERE PlayerID = 500;

-- Undoing previous query
-- Delete player from the Roster table
DELETE FROM Roster
WHERE PlayerID = 500
  AND FantasyTeamID = (SELECT FantasyTeamID FROM Fantasy_Teams WHERE ManagerName = 'Jesse');
-- Update player status to Waiver in NFL_Players
UPDATE NFL_Players
SET StatusID = (SELECT StatusID FROM Player_Status WHERE StatusName = 'Waiver')
WHERE PlayerID = 500;


-- query e
SELECT COUNT(*) AS TeamCount
FROM Fantasy_Teams;


-- query f
SELECT f.TeamName, 
       f.ManagerName, 
       p.Name, 
       p.Position, 
       rs.StatusName AS LineupStatus
FROM Fantasy_Teams f
JOIN Roster r ON f.FantasyTeamID = r.FantasyTeamID
JOIN NFL_Players p ON r.PlayerID = p.PlayerID
JOIN Roster_Status rs ON r.StatusID = rs.StatusID
ORDER BY f.TeamName, p.Position;


-- query g
SELECT tt.TypeName AS TransactionType, 
       p.Name, 
       f.TeamName, 
       t.Date
FROM Transactions t
JOIN NFL_Players p ON t.PlayerID = p.PlayerID
JOIN Fantasy_Teams f ON t.FantasyTeamID = f.FantasyTeamID
JOIN Transaction_Type tt ON t.TransactionTypeID = tt.TransactionTypeID
WHERE t.Date BETWEEN '2025-09-11 00:00:00' AND '2025-09-17 23:59:59'
ORDER BY t.Date;


-- query h
SELECT p.Name, 
       p.Position, 
       SUM(s.FantasyPoints) AS TotalPoints
FROM NFL_Players p
JOIN Player_Stats s ON p.PlayerID = s.PlayerID
WHERE p.Position = 'QB'
GROUP BY p.PlayerID, p.Name, p.Position
ORDER BY TotalPoints DESC
LIMIT 5;


-- query i
WITH TopPlayers AS (
    SELECT 
        p.PlayerID,
        p.Name,
        p.Position,
        SUM(s.FantasyPoints) AS TotalPoints,
        RANK() OVER (PARTITION BY p.Position ORDER BY SUM(s.FantasyPoints) DESC) AS PlayerRank
    FROM NFL_Players p
    JOIN Player_Stats s ON p.PlayerID = s.PlayerID
    GROUP BY p.PlayerID, p.Name, p.Position
)
SELECT 
    tp.Position,
    AVG(tp.TotalPoints) AS AvgPoints
FROM TopPlayers tp
WHERE tp.PlayerRank <= 10
GROUP BY tp.Position
ORDER BY AvgPoints DESC;


-- query j
SELECT p.Name, 
       p.Position, 
       i_s.StatusCode AS Status, 
       i.InjuryType
FROM NFL_Players p
JOIN Injuries i ON p.PlayerID = i.PlayerID
JOIN Injury_Status i_s ON i.InjuryStatusID = i_s.InjuryStatusID
WHERE i_s.StatusCode IN ('O', 'Q', 'D', 'SUSP', 'P', 'IR', 'PUP');