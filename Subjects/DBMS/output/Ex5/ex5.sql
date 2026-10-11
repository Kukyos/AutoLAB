-- setup (schema/data, not itself a graded question)
CREATE TABLE URK24CS1021_users (
    id numeric(10) PRIMARY KEY CHECK (id BETWEEN 101 AND 105),
    name varchar(255), email varchar(255) UNIQUE,
    password varchar(255), phone varchar(20) UNIQUE
);
CREATE TABLE URK24CS1021_location (
    venueid numeric(10) PRIMARY KEY, name varchar(300),
    address varchar(255), city varchar(255),
    state varchar(255), country varchar(255)
);
CREATE TABLE URK24CS1021_event (
    eventid numeric(10) PRIMARY KEY, name varchar(255),
    eventdate date, eventtime timestamp,
    venueid numeric(10) REFERENCES URK24CS1021_location(venueid),
    description varchar(1000)
);
CREATE TABLE URK24CS1021_ticket (
    ticketid numeric(10) PRIMARY KEY,
    eventid numeric(10) REFERENCES URK24CS1021_event(eventid),
    userid numeric(10), price numeric(10,2),
    status varchar(50), barcode varchar(50)
);
INSERT INTO URK24CS1021_users (id, name, email, password, phone) VALUES
    (101, 'Alice Johnson', 'alice@mail.com', 'pass1', '9000000001'),
    (102, 'Bob Smith', 'bob@mail.com', 'pass2', '9000000002'),
    (103, 'Carol Lee', 'carol@mail.com', 'pass3', '9000000003'),
    (104, 'David Kim', 'david@mail.com', 'pass4', '9000000004'),
    (105, 'Ethan Brown', 'ethan@mail.com', 'pass5', '9000000005');
INSERT INTO URK24CS1021_location (venueid, name, address, city, state, country) VALUES
    (1, 'Wembley Stadium', 'Wembley', 'London', 'England', 'UK'),
    (2, 'Madison Square Garden', '4 Pennsylvania Plaza', 'New York', 'NY', 'USA'),
    (3, 'Marina Bay Sands', '10 Bayfront Ave', 'Singapore', 'Singapore', 'Singapore');
INSERT INTO URK24CS1021_event (eventid, name, eventdate, eventtime, venueid, description) VALUES
    (1, 'Sports Tournament', '2023-08-01', '2023-08-01 09:00:00', 1, 'Regional sports tournament'),
    (2, 'Tech Conference', '2023-07-20', '2023-07-20 09:00:00', 2, 'Annual tech meetup'),
    (3, 'Art Exhibition', '2023-09-05', '2023-09-05 11:00:00', 3, 'Modern art exhibition'),
    (4, 'Charity Concert', '2023-08-15', '2023-08-15 19:00:00', 1, 'Charity fundraiser concert'),
    (5, 'Startup Summit', '2023-06-10', '2023-06-10 10:00:00', 2, 'Startup pitch day');
INSERT INTO URK24CS1021_ticket (ticketid, eventid, userid, price, status, barcode) VALUES
    (1, 1, 102, 50.00, 'confirmed', 'BC5001'),
    (2, 2, 101, 200.00, 'confirmed', 'BC5002'),
    (3, 3, 103, 40.00, 'confirmed', 'BC5003'),
    (4, 3, 105, 60.00, 'confirmed', 'BC5004'),
    (5, 4, 101, 25.00, 'confirmed', 'BC5005'),
    (6, 5, 105, 90.00, 'confirmed', 'BC5006');

-- 1
SELECT name FROM URK24CS1021_users WHERE id IN
    (SELECT userid FROM URK24CS1021_ticket WHERE eventid IN
        (SELECT eventid FROM URK24CS1021_event WHERE name = 'Sports Tournament'));

-- 2
SELECT name FROM URK24CS1021_event WHERE venueid IN
    (SELECT venueid FROM URK24CS1021_location WHERE city = 'London');

-- 3
SELECT AVG(price) AS avg_price FROM URK24CS1021_ticket WHERE eventid =
    (SELECT eventid FROM URK24CS1021_event WHERE name = 'Art Exhibition');

-- 4
SELECT name FROM URK24CS1021_users u WHERE NOT EXISTS
    (SELECT 1 FROM URK24CS1021_ticket t WHERE t.userid = u.id);

-- 5
SELECT MAX(price) AS max_price FROM URK24CS1021_ticket WHERE userid =
    (SELECT id FROM URK24CS1021_users WHERE name = 'Alice Johnson');

-- 6
SELECT DISTINCT u.name FROM URK24CS1021_users u WHERE u.id IN
    (SELECT t.userid FROM URK24CS1021_ticket t WHERE t.eventid IN
        (SELECT eventid FROM URK24CS1021_event WHERE eventdate = '2023-07-20'));

-- 7
SELECT DISTINCT u.name FROM URK24CS1021_users u WHERE EXISTS
    (SELECT 1 FROM URK24CS1021_ticket t, URK24CS1021_event e, URK24CS1021_location l
     WHERE t.userid = u.id AND t.eventid = e.eventid
       AND e.venueid = l.venueid AND l.country = 'USA');

-- 8
SELECT DISTINCT e.name FROM URK24CS1021_event e WHERE e.eventid IN
    (SELECT eventid FROM URK24CS1021_ticket WHERE price < 30);

-- 9
SELECT SUM(price) AS total_revenue FROM URK24CS1021_ticket WHERE userid =
    (SELECT id FROM URK24CS1021_users WHERE name = 'Ethan Brown');

-- 10
SELECT name FROM URK24CS1021_event e WHERE EXISTS
    (SELECT 1 FROM URK24CS1021_event e2
     WHERE e2.venueid = e.venueid AND e2.eventid <> e.eventid)
ORDER BY name;