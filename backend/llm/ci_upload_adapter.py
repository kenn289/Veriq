"""CI helper: upload an adapter directory to MinIO and delete old artifacts.

Environment variables used:
  MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
  ADAPTER_DIR: path to upload (default: backend/llm/adapters/ci-lora)
  RETENTION_DAYS: optional, integer days to keep (default: 7)

This script is best-effort and exits 0 on non-fatal errors to avoid failing CI unnecessarily.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

try:
    from minio import Minio
    from minio.error import S3Error
except Exception:
    print("minio package not available; please install minio for CI upload step.")
    sys.exit(0)


def upload_dir(client: Minio, bucket: str, adapter_dir: Path) -> None:
    if not adapter_dir.exists():
        print(f"Adapter dir {adapter_dir} not found; skipping upload")
        return
    for p in adapter_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(adapter_dir.parent)
            obj_name = rel.as_posix()
            try:
                client.fput_object(bucket, obj_name, str(p))
                print(f"Uploaded {p} -> {bucket}/{obj_name}")
            except Exception as e:
                print(f"Failed to upload {p}: {e}")


def cleanup_old_objects(client: Minio, bucket: str, prefix: str, days: int) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"Cleaning up objects in {bucket} with prefix {prefix} older than {days} days (cutoff={cutoff})")
    try:
        objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    except Exception as e:
        print(f"Failed to list objects for cleanup: {e}")
        return
    to_delete = []
    for obj in objects:
        # obj.last_modified is datetime
        if getattr(obj, "last_modified", None) and obj.last_modified < cutoff:
            to_delete.append(obj.object_name)

    for name in to_delete:
        try:
            client.remove_object(bucket, name)
            print(f"Deleted old object: {name}")
        except Exception as e:
            print(f"Failed to delete {name}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup; do not upload files")
    args = parser.parse_args()

    endpoint = os.environ.get("MINIO_ENDPOINT")
    access = os.environ.get("MINIO_ACCESS_KEY")
    secret = os.environ.get("MINIO_SECRET_KEY")
    bucket = os.environ.get("MINIO_BUCKET", "veriq-artifacts")
    adapter_dir = Path(os.environ.get("ADAPTER_DIR", "backend/llm/adapters/ci-lora"))
    retention_days = int(os.environ.get("RETENTION_DAYS", "7"))

    if not endpoint or not access or not secret:
        print("MinIO credentials not provided; skipping upload/cleanup step.")
        return

    # Strip scheme for Minio client
    ep = endpoint
    if ep.startswith("http://"):
        ep = ep[len("http://"):]
    if ep.startswith("https://"):
        ep = ep[len("https://"):]

    client = Minio(ep, access_key=access, secret_key=secret, secure=False)

    try:
        if not client.bucket_exists(bucket):
            print(f"Bucket {bucket} does not exist. Creating.")
            client.make_bucket(bucket)
    except Exception as e:
        print(f"Could not ensure bucket exists: {e}")
        return

    if not args.cleanup_only:
        upload_dir(client, bucket, adapter_dir)

    # cleanup using prefix relative to repo root: adapters/
    prefix = adapter_dir.parent.name + "/"
    cleanup_old_objects(client, bucket, prefix, retention_days)


if __name__ == "__main__":
    main()
