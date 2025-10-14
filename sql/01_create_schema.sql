CREATE DATABASE IF NOT EXISTS FantasyFootballDB;
USE FantasyFootballDB;

-- Drop existing tables (to rebuild cleanly)
DROP TABLE IF EXISTS Injuries;
DROP TABLE IF EXISTS Injury_Status;
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS Transaction_Type;
DROP TABLE IF EXISTS Player_Stats;
DROP TABLE IF EXISTS Roster;
DROP TABLE IF EXISTS Roster_Status;
DROP TABLE IF EXISTS NFL_Players;
DROP TABLE IF EXISTS Fantasy_Teams;
DROP TABLE IF EXISTS Player_Status;

-- Fantasy Teams
CREATE TABLE Fantasy_Teams (
    FantasyTeamID INT PRIMARY KEY,
    TeamName VARCHAR(50) NOT NULL,
    ManagerName VARCHAR(50) NOT NULL
);

-- NFL Players (and their status of rostered or waivered)
CREATE TABLE Player_Status (
    StatusID INT PRIMARY KEY AUTO_INCREMENT,
    StatusName VARCHAR(20) UNIQUE NOT NULL
);

INSERT INTO Player_Status (StatusName) VALUES
('Rostered'),
('Waiver');

CREATE TABLE NFL_Players (
    PlayerID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Position VARCHAR(10) NOT NULL,
    NFLTeam CHAR(3) NOT NULL,
    StatusID INT NOT NULL,
    FOREIGN KEY (StatusID) 
        REFERENCES Player_Status(StatusID)
);

-- Roster (including preset Roster_Status values)
CREATE TABLE Roster_Status (
    StatusID INT PRIMARY KEY AUTO_INCREMENT,
    StatusName VARCHAR(10) UNIQUE NOT NULL
);

INSERT INTO Roster_Status (StatusName) VALUES
('Starter'),
('Bench'),
('IR');

CREATE TABLE Roster (
    RosterID INT PRIMARY KEY auto_increment,
    FantasyTeamID INT NOT NULL,
    PlayerID INT NOT NULL UNIQUE,
    StatusID INT NOT NULL,
    FOREIGN KEY (FantasyTeamID) 
        REFERENCES Fantasy_Teams(FantasyTeamID),
    FOREIGN KEY (PlayerID) 
        REFERENCES NFL_Players(PlayerID),
    FOREIGN KEY (StatusID) 
        REFERENCES Roster_Status(StatusID)
);

-- Player Stats
CREATE TABLE Player_Stats (
    StatID INT PRIMARY KEY,
    PlayerID INT NOT NULL,
    Week INT NOT NULL,
    FantasyPoints DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (PlayerID) 
        REFERENCES NFL_Players(PlayerID)
);

-- Transactions (and what type of move it was)
CREATE TABLE Transaction_Type (
    TransactionTypeID INT PRIMARY KEY AUTO_INCREMENT,
    TypeName VARCHAR(10) UNIQUE NOT NULL
);

INSERT INTO Transaction_Type (TypeName) VALUES
('Add'),
('Drop'),
('Trade');

CREATE TABLE Transactions (
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    FantasyTeamID INT NOT NULL,
    PlayerID INT NOT NULL,
    TransactionTypeID INT NOT NULL,
    Date DATETIME NOT NULL,
    FOREIGN KEY (FantasyTeamID) 
        REFERENCES Fantasy_Teams(FantasyTeamID),
    FOREIGN KEY (PlayerID) 
        REFERENCES NFL_Players(PlayerID),
    FOREIGN KEY (TransactionTypeID) 
        REFERENCES Transaction_Type(TransactionTypeID)
);

-- Injuries (and status)
CREATE TABLE Injury_Status (
    InjuryStatusID INT PRIMARY KEY AUTO_INCREMENT,
    StatusCode VARCHAR(5) UNIQUE NOT NULL
);

INSERT INTO Injury_Status (StatusCode) VALUES
('O'),
('Q'),
('D'),
('SUSP'),
('P'),
('IR'),
('PUP');

CREATE TABLE Injuries (
    InjuryID INT PRIMARY KEY AUTO_INCREMENT,
    PlayerID INT NOT NULL,
    InjuryStatusID INT NOT NULL,
    InjuryType VARCHAR(50),
    FOREIGN KEY (PlayerID) 
        REFERENCES NFL_Players(PlayerID),
    FOREIGN KEY (InjuryStatusID) 
        REFERENCES Injury_Status(InjuryStatusID)
);

