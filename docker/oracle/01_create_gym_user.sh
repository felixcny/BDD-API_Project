#!/bin/bash

# Ce script est exécuté automatiquement par le conteneur Oracle
# lors de la première initialisation de la base.

sqlplus -s / as sysdba <<SQL

-- On se place dans la PDB utilisée par notre application.
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Création de l'utilisateur applicatif.
CREATE USER gym_app
IDENTIFIED BY "${GYM_DB_PASSWORD}"
DEFAULT TABLESPACE users
QUOTA UNLIMITED ON users;

-- Droits nécessaires à SQLAlchemy, Alembic et aux triggers.
GRANT CREATE SESSION,
      CREATE TABLE,
      CREATE VIEW,
      CREATE SEQUENCE,
      CREATE PROCEDURE,
      CREATE TRIGGER
TO gym_app;

EXIT;
SQL