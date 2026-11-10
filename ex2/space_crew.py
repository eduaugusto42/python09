#!/usr/bin/env python3
"""Exercise 2: Space Crew Management.

Nested Pydantic models and mission-level safety validation.
"""

from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    model_validator,
)


class Rank(Enum):
    """Crew ranks, from lowest to highest."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """A single crew member assigned to a mission."""

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """A mission and the crew assigned to it."""

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self) -> "SpaceMission":
        """Enforce the safety rules for a mission and its crew."""
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        if not any(
            member.rank in (Rank.CAPTAIN, Rank.COMMANDER)
            for member in self.crew
        ):
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced_count = sum(
                member.years_experience >= 5 for member in self.crew
            )
            if experienced_count * 2 < len(self.crew):
                raise ValueError(
                    "Long missions need 50% experienced crew"
                )

        if not all(member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")

        return self


def main() -> None:
    """Demonstrate one valid mission and one invalid mission."""
    print("Space Mission Crew Validation")
    print("=" * 41)

    sarah = CrewMember(
        member_id="CM001",
        name="Sarah Connor",
        rank=Rank.COMMANDER,
        age=40,
        specialization="Mission Command",
        years_experience=15,
    )

    john = CrewMember(
        member_id="CM002",
        name="John Smith",
        rank=Rank.LIEUTENANT,
        age=35,
        specialization="Navigation",
        years_experience=8,
    )

    alice = CrewMember(
        member_id="CM003",
        name="Alice Johnson",
        rank=Rank.OFFICER,
        age=30,
        specialization="Engineering",
        years_experience=5,
    )

    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 11, 1, 9, 0),
        duration_days=900,
        crew=[sarah, john, alice],
        budget_millions=2500.0,
    )

    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"- {member.name} ({member.rank.value}) - "
            f"{member.specialization}"
        )

    print("\n" + "=" * 41)
    print("Expected validation error:")

    try:
        SpaceMission(
            mission_id="M2026_TEST",
            mission_name="Training Mission",
            destination="Moon",
            launch_date=datetime(2026, 12, 1, 9, 0),
            duration_days=30,
            crew=[john, alice],
            budget_millions=50.0,
        )
    except ValidationError as error:
        for issue in error.errors():
            print(issue["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
