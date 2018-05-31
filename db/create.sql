drop table if exists ice;

CREATE TABLE ice (
  timestamp timestamp,
  location geography(POINT),
  concentration numeric(4, 1),
  speed numeric(4, 1),
  direction numeric(4, 1),
  thickness numeric(4, 1),
  PRIMARY KEY(timestamp, location)
);

drop table if exists weatherfile;

create table weatherfile (
  name varchar PRIMARY KEY,
  loadtime timestamp
);