/*
  Filename: create.sql
  Author(s): Abrar Rahman Protyasha <aprotyas>, Uzair Tahamid Siam <usiam>

  This SQL file creates the named tables in the `soctix` database.
*/

CREATE DATABASE IF NOT EXISTS soctix;

USE soctix;

CREATE TABLE IF NOT EXISTS `Customer` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `FName` VARCHAR(40),
  `LName` VARCHAR(40),
  `Username` VARCHAR(40) NOT NULL,
  `Password` VARCHAR(20) NOT NULL,
  `Email` VARCHAR(40) NOT NULL,
  `Street` VARCHAR(40),
  `City` VARCHAR(40),
  `State` CHAR(2),
  `Phone` CHAR(10),
  PRIMARY KEY (`ID`),
  UNIQUE (`Username`),
  UNIQUE (`Email`));

CREATE TABLE IF NOT EXISTS `Transaction` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Time` DATETIME,
  `C_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  CONSTRAINT `customer_id`
    FOREIGN KEY (`C_ID`) REFERENCES Customer (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `Team` (
  `ID` INT NOT NULL,
  `Name` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`ID`));

CREATE TABLE IF NOT EXISTS `TeamManager` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `T_ID` INT NOT NULL,
  `FName` VARCHAR(40),
  `LName` VARCHAR(40),
  `Username` VARCHAR(40) NOT NULL,
  `Password` VARCHAR(20) NOT NULL,
  `Email` VARCHAR(40) NOT NULL,
  `Phone` CHAR(10),
  PRIMARY KEY (`ID`),
  UNIQUE (`Username`),
  UNIQUE (`Email`),
  CONSTRAINT `team_id`
    FOREIGN KEY (`T_ID`) REFERENCES Team (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `Employee` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `FName` VARCHAR(40),
  `LName` VARCHAR(40),
  `Username` VARCHAR(40) NOT NULL,
  `Password` VARCHAR(20) NOT NULL,
  `Email` VARCHAR(40) NOT NULL,
  `Phone` CHAR(10),
  PRIMARY KEY (`ID`),
  UNIQUE (`Username`),
  UNIQUE (`Email`));

CREATE TABLE IF NOT EXISTS `Venue` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(40) NOT NULL,
  `Capacity` INT NOT NULL CHECK (`Capacity` > 0),
  `City` VARCHAR(40) NOT NULL,
  `State` CHAR(2) NOT NULL,
  PRIMARY KEY (`ID`));

CREATE TABLE IF NOT EXISTS `Event` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `Time` DATETIME NOT NULL,
  `V_ID` INT NOT NULL,
  `T1_ID` INT NOT NULL,
  `T2_ID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  CONSTRAINT `venue_id`
    FOREIGN KEY (`V_ID`) REFERENCES Venue (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `team1_id`
    FOREIGN KEY (`T1_ID`) REFERENCES Team (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `team2_id`
    FOREIGN KEY (`T2_ID`) REFERENCES Team (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `Ticket` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `T_ID` INT,
  `Em_ID` INT,
  `Ev_ID` INT NOT NULL,
  `Price` FLOAT NOT NULL CHECK (`Price` > 0.0),
  `Seat` INT NOT NULL CHECK (`Seat` > 0), /* Stadium seat numbers, strictly-positive */
  PRIMARY KEY (`ID`),
  UNIQUE (`Seat`, `Ev_ID`), /* Can't have multiple tickets to an event with the same seat */
  CONSTRAINT `transaction_id`
    FOREIGN KEY (`T_ID`) REFERENCES Transaction (`ID`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `employee_id`
    FOREIGN KEY (`Em_ID`) REFERENCES Employee (`ID`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `event_id`
    FOREIGN KEY (`Ev_ID`) REFERENCES Event (`ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
