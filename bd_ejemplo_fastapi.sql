DROP TABLE alumno;
CREATE TABLE alumno(
    rut NUMBER(8) PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) NOT NULL
);
INSERT INTO alumno VALUES(12222,'Lalo','lalo@gmail.com');
INSERT INTO alumno VALUES(13333,'Elvis','elvis@gmail.com');
INSERT INTO alumno VALUES(14444,'Maria','maria@gmail.com');
COMMIT;