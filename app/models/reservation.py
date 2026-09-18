from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Reservation(Base):
    # Nom de la table dans Oracle
    __tablename__ = "reservation"

    # Identifiant généré automatiquement par Oracle
    reservation_id: Mapped[int] = mapped_column(
        Identity(always=False, on_null=True),
        primary_key=True,
    )

    # Utilisateur qui effectue la réservation
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey(
            "utilisateur.utilisateur_id",
            name="fk_reservation_utilisateur",
        ),
        nullable=False,
    )

    # Séance réservée
    seance_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seance.seance_id",
            name="fk_reservation_seance",
        ),
        nullable=False,
    )

    # Date de création de la réservation
    # Oracle utilise SYSDATE si aucune date n'est fournie
    date_reservation: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("SYSDATE"),
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    __table_args__ = (
        # Empêche un utilisateur de réserver deux fois la même séance
        UniqueConstraint(
            "utilisateur_id",
            "seance_id",
            name="uq_reservation_utilisateur_seance",
        ),

        # Seuls ces deux statuts sont autorisés
        CheckConstraint(
            "statut IN ('CONFIRMEE', 'ANNULEE')",
            name="chk_reservation_statut",
        ),
    )