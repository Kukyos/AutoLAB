-- 1
DO $$
DECLARE
    n INT := 10;
    i INT := 1;
    total INT := 0;
BEGIN
    WHILE i <= n LOOP
        RAISE NOTICE '%', i;
        total := total + i;
        i := i + 1;
    END LOOP;
    RAISE NOTICE 'Sum of first % natural numbers = %', n, total;
END $$;

-- 2
DO $$
DECLARE
    num INT := 12345;
    temp INT;
    digit_sum INT := 0;
BEGIN
    temp := num;
    WHILE temp > 0 LOOP
        digit_sum := digit_sum + (temp % 10);
        temp := temp / 10;
    END LOOP;
    RAISE NOTICE 'Sum of digits of % = %', num, digit_sum;
END $$;

-- 3
DO $$
DECLARE
    n INT := 10;
    a INT := 0;
    b INT := 1;
    nxt INT;
    i INT;
BEGIN
    RAISE NOTICE '%', a;
    RAISE NOTICE '%', b;
    FOR i IN 3..n LOOP
        nxt := a + b;
        RAISE NOTICE '%', nxt;
        a := b;
        b := nxt;
    END LOOP;
END $$;

-- 4
DO $$
DECLARE
    a INT := 10;
    b INT := 0;
    result INT;
BEGIN
    result := a / b;
    RAISE NOTICE 'Result = %', result;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Error: division by zero is not allowed';
END $$;

-- 5
DO $$
DECLARE
    num1 NUMERIC := 20;
    num2 NUMERIC := 4;
    op CHAR(1) := '*';
    result NUMERIC;
BEGIN
    IF op = '+' THEN
        result := num1 + num2;
    ELSIF op = '-' THEN
        result := num1 - num2;
    ELSIF op = '*' THEN
        result := num1 * num2;
    ELSIF op = '/' THEN
        result := num1 / num2;
    ELSE
        RAISE NOTICE 'Invalid operator';
    END IF;
    RAISE NOTICE '% % % = %', num1, op, num2, result;
END $$;

-- 6
CREATE OR REPLACE PROCEDURE URK24CS1021_circle_area(radius NUMERIC)
LANGUAGE plpgsql AS $$
DECLARE
    pi_val CONSTANT NUMERIC := 3.14159265358979;
    area NUMERIC;
BEGIN
    area := pi_val * radius * radius;
    RAISE NOTICE 'Area of circle with radius % = %', radius, round(area, 2);
END;
$$;
CALL URK24CS1021_circle_area(7);

-- 7
CREATE OR REPLACE FUNCTION URK24CS1021_rectangle_area(length NUMERIC, width NUMERIC)
RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
    area NUMERIC;
BEGIN
    area := length * width;
    RETURN area;
END;
$$;
SELECT URK24CS1021_rectangle_area(5, 10) AS rectangle_area;