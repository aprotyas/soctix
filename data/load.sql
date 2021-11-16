/*
  Filename: load.sql
  Author(s): Abrar Rahman Protyasha <aprotyas>, Uzair Tahamid Siam <usiam>

  This SQL file loads the relevant comma-separated value data into the
  named tables in the `soctix` database.
*/

USE soctix;

/*
  Ignoring the first line for all imports, so that
  we can retain the column name metadata in the
  original CSV files.

  Also, if a row with a given PK exists, its ignored
  during import.
*/

LOAD DATA LOCAL INFILE './Customer.csv'
  IGNORE INTO TABLE Customer
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Transaction.csv'
  IGNORE INTO TABLE Transaction
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Team.csv'
  IGNORE INTO TABLE Team
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './TeamManager.csv'
  IGNORE INTO TABLE TeamManager
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Employee.csv'
  IGNORE INTO TABLE Employee
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Venue.csv'
  IGNORE INTO TABLE Venue
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Event.csv'
  IGNORE INTO TABLE Event
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;

LOAD DATA LOCAL INFILE './Ticket.csv'
  IGNORE INTO TABLE Ticket
  FIELDS TERMINATED BY ','
  IGNORE 1 LINES;
