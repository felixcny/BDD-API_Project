from sqlalchemy import ForeignKey, Identity, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Coach(Base):
    # Nom de la table dans Oracle
    __tablename__ = "coach"

    # Identifiant du profil coach, généré automatiquement par Oracle
    coach_id: Mapped[int] = mapped_column(
        Identity(always=False, on_null=True),
        primary_key=True,
    )

    # Un coach est lié à un utilisateur existant
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey(
            "utilisateur.utilisateur_id",
            name="fk_coach_utilisateur",
        ),
        nullable=False,
    )

    # Domaine ou spécialité du coach
    specialite: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Un même utilisateur ne peut avoir qu'un seul profil coach
    __table_args__ = (
        UniqueConstraint(
            "utilisateur_id",
            name="uq_coach_utilisateur",
        ),
    )