"""Standalone CLI to run the CSV processing pipeline.

Usage:
    python -m app.run_pipeline [--csv path/to/file.csv]
"""
import argparse
import logging
import sys
from app.config import settings
from app.database import SessionLocal, engine, Base
from app.services.pipeline import run_pipeline

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Run the scenario CSV processing pipeline")
    parser.add_argument("--csv", default=settings.csv_path, help="Path to scenarios CSV file")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        result = run_pipeline(args.csv, db)
        print(f"Pipeline complete: {result}")
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
