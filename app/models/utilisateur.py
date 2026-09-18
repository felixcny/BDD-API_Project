from datetime import date

from sqlalchemy import CheckConstraint, Date, Identity, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Utilisateur(Base):
    # Nom exact de la table Oracle
    __tablename__ = "utilisateur"

    # Identifiant généré automatiquement par Oracle
    utilisateur_id: Mapped[int] = mapped_column(
        Identity(always=False, on_null=True),
        primary_key=True,
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prenom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # L'adresse email doit être unique pour chaque utilisateur
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # On stocke uniquement le hash du mot de passe, jamais le mot de passe brut
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Oracle utilise SYSDATE automatiquement si aucune date n'est fournie
    date_inscription: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("SYSDATE"),
    )

    # Contraintes supplémentaires imposées directement par la base
    __table_args__ = (
        CheckConstraint(
            "role IN ('MEMBRE', 'COACH', 'ADMIN')",
            name="chk_utilisateur_role",
        ),
    )