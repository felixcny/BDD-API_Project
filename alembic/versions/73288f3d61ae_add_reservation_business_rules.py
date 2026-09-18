"""add reservation business rules

Revision ID: 73288f3d61ae
Revises: 22f6950652ff
Create Date: 2026-09-18 10:32:29.528031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73288f3d61ae'
down_revision: Union[str, Sequence[str], None] = '22f6950652ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Récupère directement la connexion Oracle utilisée par Alembic.
    # exec_driver_sql permet d'envoyer du PL/SQL Oracle sans que SQLAlchemy
    # interprète :NEW comme un paramètre Python.
    connection = op.get_bind()

    # ------------------------------------------------------------------
    # RÈGLE 1 :
    # Une réservation CONFIRMEE nécessite un abonnement ACTIF
    # couvrant la date de la séance.
    # ------------------------------------------------------------------
    connection.exec_driver_sql(
        """
        CREATE OR REPLACE TRIGGER trg_reservation_abonnement
        BEFORE INSERT OR UPDATE OF utilisateur_id, seance_id, statut
        ON reservation
        FOR EACH ROW
        WHEN (NEW.statut = 'CONFIRMEE')
        DECLARE
            v_date_seance DATE;
            v_nb_abonnements NUMBER;
        BEGIN
            -- Récupère la date de la séance que l'utilisateur veut réserver.
            SELECT CAST(date_heure AS DATE)
            INTO v_date_seance
            FROM seance
            WHERE seance_id = :NEW.seance_id;

            -- Cherche un abonnement ACTIF couvrant cette date.
            SELECT COUNT(*)
            INTO v_nb_abonnements
            FROM abonnement
            WHERE utilisateur_id = :NEW.utilisateur_id
              AND statut = 'ACTIF'
              AND TRUNC(v_date_seance)
                  BETWEEN TRUNC(date_debut) AND TRUNC(date_fin);

            -- Aucun abonnement valide : réservation refusée.
            IF v_nb_abonnements = 0 THEN
                RAISE_APPLICATION_ERROR(
                    -20001,
                    'Reservation impossible : aucun abonnement actif pour cette seance.'
                );
            END IF;
        END;
        """
    )

    # ------------------------------------------------------------------
    # RÈGLE 2 :
    # Le nombre de réservations CONFIRMEES ne doit jamais dépasser
    # la capacité maximale de la séance.
    #
    # On utilise un COMPOUND TRIGGER car un trigger ligne classique
    # ne peut pas relire proprement la table RESERVATION pendant
    # qu'elle est en cours de modification (problème de table mutante).
    # ------------------------------------------------------------------
    connection.exec_driver_sql(
        """
        CREATE OR REPLACE TRIGGER trg_reservation_capacite
        FOR INSERT OR UPDATE OF seance_id, statut
        ON reservation
        COMPOUND TRIGGER

            -- Ensemble des séances qu'il faudra vérifier après l'opération.
            TYPE t_seances IS TABLE OF BOOLEAN INDEX BY VARCHAR2(50);
            g_seances t_seances;

            BEFORE EACH ROW IS
                v_capacite seance.capacite_max%TYPE;
            BEGIN
                -- Seules les réservations confirmées utilisent une place.
                IF :NEW.statut = 'CONFIRMEE' THEN

                    -- Verrouille la séance pendant la réservation.
                    -- Cela évite que deux transactions dépassent
                    -- simultanément la capacité maximale.
                    SELECT capacite_max
                    INTO v_capacite
                    FROM seance
                    WHERE seance_id = :NEW.seance_id
                    FOR UPDATE;

                    -- Mémorise la séance à vérifier.
                    g_seances(TO_CHAR(:NEW.seance_id)) := TRUE;
                END IF;
            END BEFORE EACH ROW;


            AFTER STATEMENT IS
                v_cle VARCHAR2(50);
                v_seance_id NUMBER;
                v_capacite NUMBER;
                v_nb_confirmees NUMBER;
            BEGIN
                v_cle := g_seances.FIRST;

                WHILE v_cle IS NOT NULL LOOP

                    v_seance_id := TO_NUMBER(v_cle);

                    -- Capacité maximale définie pour la séance.
                    SELECT capacite_max
                    INTO v_capacite
                    FROM seance
                    WHERE seance_id = v_seance_id;

                    -- Nombre réel de réservations confirmées.
                    SELECT COUNT(*)
                    INTO v_nb_confirmees
                    FROM reservation
                    WHERE seance_id = v_seance_id
                      AND statut = 'CONFIRMEE';

                    -- Si la capacité est dépassée, Oracle annule l'opération.
                    IF v_nb_confirmees > v_capacite THEN
                        RAISE_APPLICATION_ERROR(
                            -20002,
                            'Reservation impossible : capacite maximale atteinte.'
                        );
                    END IF;

                    v_cle := g_seances.NEXT(v_cle);
                END LOOP;
            END AFTER STATEMENT;

        END;
        """
    )

    # ------------------------------------------------------------------
    # RÈGLE 3A :
    # Un utilisateur associé à la table COACH doit avoir le rôle COACH.
    # ------------------------------------------------------------------
    connection.exec_driver_sql(
        """
        CREATE OR REPLACE TRIGGER trg_coach_role
        BEFORE INSERT OR UPDATE OF utilisateur_id
        ON coach
        FOR EACH ROW
        DECLARE
            v_role utilisateur.role%TYPE;
        BEGIN
            -- Récupère le rôle de l'utilisateur concerné.
            SELECT role
            INTO v_role
            FROM utilisateur
            WHERE utilisateur_id = :NEW.utilisateur_id;

            -- Refuse la création du profil coach si le rôle ne correspond pas.
            IF v_role <> 'COACH' THEN
                RAISE_APPLICATION_ERROR(
                    -20003,
                    'Profil coach impossible : utilisateur sans role COACH.'
                );
            END IF;
        END;
        """
    )

    # ------------------------------------------------------------------
    # RÈGLE 3B :
    # Empêche de retirer le rôle COACH à un utilisateur possédant
    # déjà un profil dans la table COACH.
    # ------------------------------------------------------------------
    connection.exec_driver_sql(
        """
        CREATE OR REPLACE TRIGGER trg_utilisateur_role_coach
        BEFORE UPDATE OF role
        ON utilisateur
        FOR EACH ROW
        WHEN (OLD.role = 'COACH' AND NEW.role <> 'COACH')
        DECLARE
            v_nb_profils NUMBER;
        BEGIN
            -- Vérifie si cet utilisateur possède un profil coach.
            SELECT COUNT(*)
            INTO v_nb_profils
            FROM coach
            WHERE utilisateur_id = :OLD.utilisateur_id;

            IF v_nb_profils > 0 THEN
                RAISE_APPLICATION_ERROR(
                    -20004,
                    'Modification impossible : cet utilisateur possede un profil coach.'
                );
            END IF;
        END;
        """
    )


def downgrade() -> None:
    # Supprime les triggers si on revient à la migration précédente.
    connection = op.get_bind()

    connection.exec_driver_sql(
        "DROP TRIGGER trg_utilisateur_role_coach"
    )

    connection.exec_driver_sql(
        "DROP TRIGGER trg_coach_role"
    )

    connection.exec_driver_sql(
        "DROP TRIGGER trg_reservation_capacite"
    )

    connection.exec_driver_sql(
        "DROP TRIGGER trg_reservation_abonnement"
    )