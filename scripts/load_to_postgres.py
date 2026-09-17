"""Generate and load the MVP dataset into local PostgreSQL."""

import os

from ai_operations_copilot.database import load_dataset
from ai_operations_copilot.synthetic_data import generate_dataset


def main() -> None:
    connection_string = os.environ.get(
        "DATABASE_URL",
        "postgresql://ai_operations:change-me-locally@localhost:5432/ai_operations",
    )
    load_dataset(generate_dataset(), connection_string)
    print("Loaded Synthetic Data into PostgreSQL")


if __name__ == "__main__":
    main()
