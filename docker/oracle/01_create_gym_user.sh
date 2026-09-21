#!/bin/bash
set -e

# Ce script est exécuté après le démarrage d'Oracle.
# Il doit pouvoir être relancé plusieurs fois sans provoquer d'erreur.

echo "[oracle-init] Verification de l'utilisateur gym_app..."

sqlplus -s / as sysdba <<SQL

-- Si une commande SQL échoue réellement, SQL*Plus renvoie une erreur.
WHENEVER SQLERROR EXIT SQL.SQLCODE

-- Notre application utilise la PDB FREEPDB1.
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Création de gym_app uniquement s'il n'existe pas encore.
DECLARE
    v_nb_utilisateurs NUMBER;
BEGIN
    SELECT COUNT(*)
    INTO v_nb_utilisateurs
    FROM dba_users
    WHERE username = 'GYM_APP';

    IF v_nb_utilisateurs = 0 THEN
        EXECUTE IMMEDIATE
            'CREATE USER gym_app IDENTIFIED BY "${GYM_DB_PASSWORD}" ' ||
            'DEFAULT TABLESPACE users QUOTA UNLIMITED ON users';
    END IF;
END;
/

-- On synchronise également son mot de passe avec le .env.
-- Ainsi, le script reste valable même après un redémarrage.
ALTER USER gym_app
IDENTIFIED BY "${GYM_DB_PASSWORD}"
ACCOUNT UNLOCK;

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

echo "[oracle-init] gym_app est pret."