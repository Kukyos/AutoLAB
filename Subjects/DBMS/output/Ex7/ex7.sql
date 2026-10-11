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
    (103, 'Carol Lee', 'carol@mail.com', 'pass3', '9000000003');
INSERT INTO URK24CS1021_location (venueid, name, address, city, state, country) VALUES
    (1, 'Wembley Stadium', 'Wembley', 'London', 'England', 'UK'),
    (2, 'Madison Square Garden', '4 Pennsylvania Plaza', 'New York', 'NY', 'USA'),
    (3, 'Marina Bay Sands', '10 Bayfront Ave', 'Singapore', 'Singapore', 'Singapore'),
    (4, 'City Arena', '1 Main St', 'Chicago', 'IL', 'USA'),
    (5, 'Grand Theater', '5 Broadway', 'New York', 'NY', 'USA');
INSERT INTO URK24CS1021_event (eventid, name, eventdate, eventtime, venueid, description) VALUES
    (1, 'Jazz Night', '2023-09-05', '2023-09-05 20:00:00', 3, 'Live jazz performance'),
    (2, 'Startup Summit', '2023-06-10', '2023-06-10 10:00:00', 2, 'Startup pitch day'),
    (3, 'Book Fair', '2024-01-12', '2024-01-12 10:00:00', 4, 'National book fair');
INSERT INTO URK24CS1021_ticket (ticketid, eventid, userid, price, status, barcode) VALUES
    (1, 1, 101, 100.00, 'reserved', 'BC7001'),
    (2, 2, 102, 150.00, 'confirmed', 'BC7002');

-- 1
CREATE OR REPLACE FUNCTION URK24CS1021_conf_venue_fn() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.name ILIKE '%Conference%' THEN
        NEW.venueid := 5;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER URK24CS1021_t1_conf_venue
BEFORE INSERT ON URK24CS1021_event
FOR EACH ROW EXECUTE FUNCTION URK24CS1021_conf_venue_fn();
INSERT INTO URK24CS1021_event (eventid, name, eventdate, eventtime, venueid, description)
VALUES (4, 'AI Conference', '2023-10-10', '2023-10-10 09:00:00', 2, 'Annual AI conference');
SELECT eventid, name, venueid FROM URK24CS1021_event WHERE eventid = 4;

-- 2
CREATE OR REPLACE FUNCTION URK24CS1021_venue_del_fn() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE URK24CS1021_event SET venueid = NULL WHERE venueid = OLD.venueid;
    RETURN OLD;
END;
$$;
CREATE TRIGGER URK24CS1021_t2_venue_del
BEFORE DELETE ON URK24CS1021_location
FOR EACH ROW EXECUTE FUNCTION URK24CS1021_venue_del_fn();
DELETE FROM URK24CS1021_location WHERE venueid = 3;
SELECT eventid, name, venueid FROM URK24CS1021_event WHERE eventid = 1;

-- 3
CREATE OR REPLACE FUNCTION URK24CS1021_venue_change_fn() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Event % venue changed from % to %', OLD.eventid, OLD.venueid, NEW.venueid;
    RETURN NEW;
END;
$$;
CREATE TRIGGER URK24CS1021_t3_venue_change
AFTER UPDATE OF venueid ON URK24CS1021_event
FOR EACH ROW EXECUTE FUNCTION URK24CS1021_venue_change_fn();
UPDATE URK24CS1021_event SET venueid = 4 WHERE eventid = 2;

-- 4
CREATE OR REPLACE FUNCTION URK24CS1021_block_grand_fn() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.venueid = (SELECT venueid FROM URK24CS1021_location WHERE name = 'Grand Theater') THEN
        RAISE EXCEPTION 'Events are not allowed at Grand Theater';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER URK24CS1021_t4_block_grand
BEFORE INSERT ON URK24CS1021_event
FOR EACH ROW EXECUTE FUNCTION URK24CS1021_block_grand_fn();
INSERT INTO URK24CS1021_event (eventid, name, eventdate, eventtime, venueid, description)
VALUES (5, 'Community Play', '2023-11-01', '2023-11-01 19:00:00', 5, 'Local theater play');

-- 5
CREATE TABLE URK24CS1021_ticket_audit (
    ticketid numeric(10), eventid numeric(10), userid numeric(10),
    price numeric(10,2), status varchar(50), barcode varchar(50)
);
CREATE OR REPLACE FUNCTION URK24CS1021_ticket_audit_fn() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO URK24CS1021_ticket_audit
        VALUES (NEW.ticketid, NEW.eventid, NEW.userid, NEW.price, NEW.status, NEW.barcode);
    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'reserved' AND NEW.status = 'confirmed' THEN
        INSERT INTO URK24CS1021_ticket_audit
        VALUES (OLD.ticketid, OLD.eventid, OLD.userid, OLD.price, OLD.status, OLD.barcode);
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER URK24CS1021_t5_ticket_audit
AFTER INSERT OR UPDATE ON URK24CS1021_ticket
FOR EACH ROW EXECUTE FUNCTION URK24CS1021_ticket_audit_fn();
INSERT INTO URK24CS1021_ticket (ticketid, eventid, userid, price, status, barcode)
VALUES (3, 3, 103, 80.00, 'reserved', 'BC7003');
UPDATE URK24CS1021_ticket SET status = 'confirmed' WHERE ticketid = 1;
SELECT * FROM URK24CS1021_ticket_audit;

-- 6
ALTER TABLE URK24CS1021_ticket DISABLE TRIGGER URK24CS1021_t5_ticket_audit;
INSERT INTO URK24CS1021_ticket (ticketid, eventid, userid, price, status, barcode)
VALUES (4, 2, 102, 60.00, 'confirmed', 'BC7004');
SELECT * FROM URK24CS1021_ticket_audit;

-- 7
DROP TRIGGER URK24CS1021_t1_conf_venue ON URK24CS1021_event;
INSERT INTO URK24CS1021_event (eventid, name, eventdate, eventtime, venueid, description)
VALUES (6, 'Robotics Conference', '2023-12-01', '2023-12-01 10:00:00', 2, 'Robotics expo');
SELECT eventid, name, venueid FROM URK24CS1021_event WHERE eventid = 6;