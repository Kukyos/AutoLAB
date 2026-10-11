-- setup (schema/data, not itself a graded question)
CREATE TABLE URK24CS1021_employee (ename varchar(50) PRIMARY KEY, city varchar(50));
CREATE TABLE URK24CS1021_company (cname varchar(50), city varchar(50));
CREATE TABLE URK24CS1021_emp_company (ename varchar(50), cname varchar(50), salary numeric(10,2), jdate date);
CREATE TABLE URK24CS1021_manager (ename varchar(50), mname varchar(50));
CREATE TABLE URK24CS1021_emp_shift (ename varchar(50), shift varchar(5));
INSERT INTO URK24CS1021_employee (ename, city) VALUES
    ('Anil', 'Nagpur'), ('Shankar', 'Bombay'), ('Jaya', 'Chennai'),
    ('Sunil', 'Bombay'), ('Vijay', 'Delhi'), ('Prakash', 'Calcutta'),
    ('Ajay', 'Nagpur');
INSERT INTO URK24CS1021_emp_company (ename, cname, salary, jdate) VALUES
    ('Anil', 'Acc', 1500, '1989-05-01'), ('Shankar', 'TATA', 2000, '1990-07-10'),
    ('Jaya', 'CMC', 1800, '1991-06-07'), ('Sunil', 'CMC', 1700, '1988-01-01'),
    ('Vijay', 'TATA', 5000, '1988-01-03'), ('Prakash', 'TATA', 3000, '1989-05-27'),
    ('Ajay', 'CMC', 8000, '1995-04-30'), ('Amol', 'Acc', 1000, '1995-03-17'),
    ('Kiran', 'Hyundai Mobis', 30000, '1998-12-18');
INSERT INTO URK24CS1021_company (cname, city) VALUES
    ('Acc', 'Chennai'), ('TATA', 'Bombay'), ('Acc', 'Nagpur'),
    ('CMC', 'Bombay'), ('CMC', 'Chennai'), ('TATA', 'Chennai');
INSERT INTO URK24CS1021_manager (ename, mname) VALUES
    ('Anil', 'Ajay'), ('Shankar', 'Vijay'), ('Jaya', NULL),
    ('Sunil', 'Jaya'), ('Vijay', NULL), ('Prakash', 'Shankar'), ('Ajay', NULL);
INSERT INTO URK24CS1021_emp_shift (ename, shift) VALUES
    ('Anil', 'A'), ('Sunil', 'B'), ('Vijay', 'B'), ('Prakash', 'C'), ('Kiran', 'E');

-- 1
SELECT city FROM URK24CS1021_company WHERE cname = 'Acc'
UNION
SELECT city FROM URK24CS1021_company WHERE cname = 'TATA';

-- 2
SELECT city FROM URK24CS1021_company WHERE cname = 'Acc'
INTERSECT
SELECT city FROM URK24CS1021_company WHERE cname = 'TATA';

-- 3
SELECT city FROM URK24CS1021_company WHERE cname = 'Acc'
EXCEPT
SELECT city FROM URK24CS1021_company WHERE cname = 'TATA';

-- 4
SELECT ename FROM URK24CS1021_employee WHERE city = 'Nagpur'
INTERSECT
SELECT ename FROM URK24CS1021_emp_company WHERE cname = 'Acc';

-- 5
SELECT ename FROM URK24CS1021_employee WHERE city = 'Nagpur'
EXCEPT
SELECT ename FROM URK24CS1021_emp_company WHERE cname = 'Acc';

-- 6
SELECT e.ename FROM URK24CS1021_employee e, URK24CS1021_emp_company c
WHERE e.ename = c.ename AND e.city = 'Bombay' AND c.salary > 1500;

-- 7
SELECT e.ename FROM URK24CS1021_employee e, URK24CS1021_emp_company c
WHERE e.ename = c.ename AND e.city = 'Chennai' AND c.cname = 'CMC';

-- 8
SELECT ename FROM URK24CS1021_employee WHERE city = 'Nagpur'
INTERSECT
SELECT ename FROM URK24CS1021_emp_company WHERE cname = 'Acc'
INTERSECT
SELECT ename FROM URK24CS1021_emp_shift WHERE shift = 'A';

-- 9
SELECT ename FROM URK24CS1021_employee WHERE city = 'Nagpur'
INTERSECT
SELECT ename FROM URK24CS1021_emp_company WHERE cname = 'Acc'
EXCEPT
SELECT ename FROM URK24CS1021_emp_shift WHERE shift = 'B';

-- 10
SELECT ename FROM URK24CS1021_employee WHERE city = 'Nagpur'
UNION
SELECT ename FROM URK24CS1021_employee WHERE city = 'Bombay';

-- 11
SELECT ename FROM URK24CS1021_employee
UNION
SELECT ename FROM URK24CS1021_emp_company;
SELECT ename FROM URK24CS1021_employee
UNION ALL
SELECT ename FROM URK24CS1021_emp_company;

-- 12
SELECT ec.ename FROM URK24CS1021_emp_company ec, URK24CS1021_emp_shift s
WHERE ec.ename = s.ename AND ec.jdate = '1998-12-18' AND s.shift = 'E';

-- 13
SELECT ename FROM URK24CS1021_employee
WHERE city IN (SELECT city FROM URK24CS1021_employee WHERE ename = 'Sunil');

-- 14
SELECT ename FROM URK24CS1021_employee
WHERE city = 'Bombay' AND ename IN
    (SELECT ename FROM URK24CS1021_emp_company WHERE cname IN
        (SELECT cname FROM URK24CS1021_company WHERE city = 'Delhi'));

-- 15
SELECT ename FROM URK24CS1021_employee
WHERE city IN (SELECT city FROM URK24CS1021_employee WHERE ename = 'Ajay');