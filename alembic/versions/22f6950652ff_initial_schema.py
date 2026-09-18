"""initial schema"""
from sqlalchemy.dialects import oracle
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "22f6950652ff"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "UTILISATEUR",
        sa.Column(
            "utilisateur_id",
            sa.Integer(),
            sa.Identity(always=False, on_null=True),
            nullable=False,
        ),
        sa.Column("nom", sa.String(100), nullable=False),
        sa.Column("prenom", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column(
            "date_inscription",
            sa.Date(),
            server_default=sa.text("SYSDATE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("utilisateur_id"),
        sa.UniqueConstraint("email"),
        sa.CheckConstraint(
            "role IN ('MEMBRE', 'COACH', 'ADMIN')"
        ),
    )

    op.create_table(
        "ABONNEMENT",
        sa.Column(
            "abonnement_id",
            sa.Integer(),
            sa.Identity(always=False, on_null=True),
            nullable=False,
        ),
        sa.Column("utilisateur_id", sa.Integer(), nullable=False),
        sa.Column("type_abonnement", sa.String(30), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("date_fin", sa.Date(), nullable=False),
        sa.Column("prix", sa.Numeric(8, 2), nullable=False),
        sa.Column("statut", sa.String(20), nullable=False),

        sa.PrimaryKeyConstraint("abonnement_id"),

        sa.ForeignKeyConstraint(
            ["utilisateur_id"],
            ["UTILISATEUR.utilisateur_id"],
            name="fk_abonnement_utilisateur",
        ),

        sa.CheckConstraint(
            "type_abonnement IN "
            "('MENSUEL', 'TRIMESTRIEL', 'ANNUEL', 'PREMIUM')"
        ),

        sa.CheckConstraint(
            "prix > 0"
        ),

        sa.CheckConstraint(
            "statut IN ('ACTIF', 'EXPIRE', 'ANNULE')"
        ),

        sa.CheckConstraint(
            "date_fin > date_debut",
            name="chk_abonnement_dates",
        ),
    )

    op.create_table(
        "COACH",
        sa.Column(
            "coach_id",
            sa.Integer(),
            sa.Identity(always=False, on_null=True),
            nullable=False,
        ),
        sa.Column("utilisateur_id", sa.Integer(), nullable=False),
        sa.Column("specialite", sa.String(100), nullable=False),

        sa.PrimaryKeyConstraint("coach_id"),

        sa.UniqueConstraint(
            "utilisateur_id",
            name="uq_coach_utilisateur",
        ),

        sa.ForeignKeyConstraint(
            ["utilisateur_id"],
            ["UTILISATEUR.utilisateur_id"],
            name="fk_coach_utilisateur",
        ),
    )

    op.create_table(
        "SEANCE",
        sa.Column(
            "seance_id",
            sa.Integer(),
            sa.Identity(always=False, on_null=True),
            nullable=False,
        ),
        sa.Column("nom", sa.String(150), nullable=False),
        sa.Column("coach_id", sa.Integer(), nullable=False),
        # La table Oracle utilise réellement un TIMESTAMP ici
        sa.Column("date_heure", oracle.TIMESTAMP(), nullable=False),
        sa.Column("duree_min", sa.Integer(), nullable=False),
        sa.Column("capacite_max", sa.Integer(), nullable=False),

        sa.PrimaryKeyConstraint("seance_id"),

        sa.ForeignKeyConstraint(
            ["coach_id"],
            ["COACH.coach_id"],
            name="fk_seance_coach",
        ),

        sa.CheckConstraint(
            "duree_min > 0"
        ),

        sa.CheckConstraint(
            "capacite_max > 0"
        ),
    )

    op.create_table(
        "RESERVATION",
        sa.Column(
            "reservation_id",
            sa.Integer(),
            sa.Identity(always=False, on_null=True),
            nullable=False,
        ),
        sa.Column("utilisateur_id", sa.Integer(), nullable=False),
        sa.Column("seance_id", sa.Integer(), nullable=False),
        sa.Column(
            "date_reservation",
            sa.DateTime(),
            server_default=sa.text("SYSDATE"),
            nullable=False,
        ),
        sa.Column("statut", sa.String(20), nullable=False),

        sa.PrimaryKeyConstraint("reservation_id"),

        sa.ForeignKeyConstraint(
            ["utilisateur_id"],
            ["UTILISATEUR.utilisateur_id"],
            name="fk_reservation_utilisateur",
        ),

        sa.ForeignKeyConstraint(
            ["seance_id"],
            ["SEANCE.seance_id"],
            name="fk_reservation_seance",
        ),

        sa.UniqueConstraint(
            "utilisateur_id",
            "seance_id",
            name="uq_reservation_utilisateur_seance",
        ),

        sa.CheckConstraint(
            "statut IN ('CONFIRMEE', 'ANNULEE')"
        ),
    )


def downgrade() -> None:
    op.drop_table("RESERVATION")
    op.drop_table("SEANCE")
    op.drop_table("COACH")
    op.drop_table("ABONNEMENT")
    op.drop_table("UTILISATEUR")