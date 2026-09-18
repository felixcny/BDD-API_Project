from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Identity, String
from sqlalchemy.dialects.oracle import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Seance(Base):
    # Nom de la table dans Oracle
    __tablename__ = "seance"

    # Identifiant généré automatiquement par Oracle
    seance_id: Mapped[int] = mapped_column(
        Identity(always=False, on_null=True),
        primary_key=True,
    )

    # Nom de la séance
    nom: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # Coach responsable de la séance
    coach_id: Mapped[int] = mapped_column(
        ForeignKey(
            "coach.coach_id",
            name="fk_seance_coach",
        ),
        nullable=False,
    )

    # Oracle stocke la date et l'heure de la séance dans un TIMESTAMP.
    # On utilise explicitement le type Oracle pour que SQLAlchemy
    # et Alembic voient exactement le même type que dans la BDD.
    date_heure: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
    )

    # Durée en minutes
    duree_min: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Nombre maximum de participants
    capacite_max: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Contraintes directement appliquées dans la base
    __table_args__ = (
        # Une séance doit durer au moins 1 minute
        CheckConstraint(
            "duree_min > 0",
        ),

        # La capacité doit être strictement positive
        CheckConstraint(
            "capacite_max > 0",
        ),
    )