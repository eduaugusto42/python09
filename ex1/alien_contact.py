#!/usr/bin/env python3
"""Exercise 1: Alien Contact Logs.

Custom business-rule validation with Pydantic's @model_validator.
"""

from datetime import datetime
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    model_validator,
)


class ContactType(Enum):
    """The four ways an alien contact can happen."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """A single report of contact with an alien species."""

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_contact(self) -> "AlienContact":
        """Enforce the business rules for alien contact reports."""
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        if (
            self.contact_type == ContactType.TELEPATHIC
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (> 7.0) should include received messages"
            )
        return self


def main() -> None:
    """Demonstrate one valid report and one invalid report."""
    print("Alien Contact Log Validation")
    print("=" * 38)

    contact = AlienContact(
        contact_id="AC_2024_001",
        timestamp=datetime(2024, 6, 15, 21, 30),
        location="Area 51, Nevada",
        contact_type=ContactType.RADIO,
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli",
    )

    print("Valid contact report:")
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    if contact.message_received is not None:
        print(f"Message: '{contact.message_received}'")

    print("\n" + "=" * 38)
    print("Expected validation error:")

    try:
        AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime(2024, 6, 15, 21, 30),
            location="Area 51, Nevada",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=5.0,
            duration_minutes=45,
            witness_count=2,
        )
    except ValidationError as exc:
        for issue in exc.errors():
            print(issue["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
