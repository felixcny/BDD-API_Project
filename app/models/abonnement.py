from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Identity,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Abonnement(Base):
    # Nom de la table dans Oracle
    __tablename__ = "abonnement"

    # Identifiant généré automatiquement par Oracle
    abonnement_id: Mapped[int] = mapped_column(
        Identity(always=False, on_null=True),
        primary_key=True,
    )

    # Utilisateur auquel appartient l'abonnement
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey(
            "utilisateur.utilisateur_id",
            name="fk_abonnement_utilisateur",
        ),
        nullable=False,
    )

    type_abonnement: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    date_debut: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Numeric est utilisé pour conserver exactement les 2 décimales du prix
    prix: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Contraintes métier directement appliquées au niveau de la BDD
    __table_args__ = (
        # Seuls ces quatre types d'abonnement sont autorisés
        CheckConstraint(
            "type_abonnement IN "
            "('MENSUEL', 'TRIMESTRIEL', 'ANNUEL', 'PREMIUM')",
            name="chk_abonnement_type",
        ),

        # La date de fin doit obligatoirement être après la date de début
        CheckConstraint(
            "date_fin > date_debut",
            name="chk_abonnement_dates",
        ),

        # Un abonnement ne peut pas avoir un prix nul ou négatif
        CheckConstraint(
            "prix > 0",
        ),

        # Liste des statuts autorisés
        CheckConstraint(
            "statut IN ('ACTIF', 'EXPIRE', 'ANNULE')",
        ),
    )