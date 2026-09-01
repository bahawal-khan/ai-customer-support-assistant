"""End-to-end dataset pipeline: download -> validate -> clean -> dedupe -> split -> manifest.

Run directly with: python -m ml.data.pipeline
"""

from __future__ import annotations

from pathlib import Path

from ml.data.clean import clean_dataframe
from ml.data.config import MANIFEST_FILENAME, METADATA_DIR, PROCESSED_DIR, RAW_DIR, SEED
from ml.data.dedupe import deduplicate
from ml.data.download import download_raw_dataset
from ml.data.labels import build_label_mapping
from ml.data.load import load_dataset_as_dataframe
from ml.data.manifest import build_manifest, write_manifest
from ml.data.schema import validate_schema
from ml.data.split import stratified_group_split


def run_pipeline(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    metadata_dir: Path = METADATA_DIR,
    seed: int = SEED,
) -> dict:
    """Run the full Phase 02 dataset pipeline and persist processed splits + manifest.

    Returns the manifest dict.
    """
    csv_path = download_raw_dataset(raw_dir)
    raw_df = load_dataset_as_dataframe(csv_path)

    validate_schema(raw_df)
    raw_row_count = len(raw_df)

    cleaned_df, rows_removed_empty = clean_dataframe(raw_df)
    deduped_df, rows_removed_duplicate = deduplicate(cleaned_df)

    label_mapping = build_label_mapping(deduped_df)
    splits = stratified_group_split(deduped_df, seed=seed)

    processed_dir.mkdir(parents=True, exist_ok=True)
    for name, split_df in splits.items():
        split_df.to_csv(processed_dir / f"{name}.csv", index=False)

    manifest = build_manifest(
        raw_row_count=raw_row_count,
        rows_removed_empty=rows_removed_empty,
        rows_removed_duplicate=rows_removed_duplicate,
        cleaned_row_count=len(deduped_df),
        label_mapping=label_mapping,
        splits=splits,
        seed=seed,
    )
    write_manifest(manifest, metadata_dir / MANIFEST_FILENAME)

    return manifest


def _print_summary(manifest: dict) -> None:
    row_counts = manifest["row_counts"]
    print(f"Raw rows: {row_counts['raw']}")
    print(f"Removed (empty): {row_counts['removed_empty']}")
    print(f"Removed (duplicate): {row_counts['removed_duplicate']}")
    print(f"Cleaned rows: {row_counts['cleaned']}")
    for name, count in row_counts["splits"].items():
        print(f"  {name}: {count} rows")
    print(f"Classes: {len(manifest['label_mapping'])}")


if __name__ == "__main__":
    result_manifest = run_pipeline()
    _print_summary(result_manifest)
