"""Generate CSV extracts for local inspection and Power BI prototyping."""

from pathlib import Path

from ai_operations_copilot.synthetic_data import DatasetConfig, generate_dataset


def main() -> None:
    output_dir = Path("data/generated")
    power_bi_dir = output_dir / "powerbi"
    output_dir.mkdir(parents=True, exist_ok=True)
    power_bi_dir.mkdir(parents=True, exist_ok=True)
    dataset = generate_dataset(DatasetConfig())
    for table_name, frame in dataset.items():
        frame.to_csv(output_dir / f"{table_name}.csv", index=False)
        frame.to_csv(power_bi_dir / f"{table_name}.csv", index=False, sep=";", decimal=",")
        print(f"{table_name}: {len(frame):,} rows")
    print(f"Power BI files: {power_bi_dir}")


if __name__ == "__main__":
    main()
