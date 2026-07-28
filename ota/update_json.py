#!/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime, timezone

REPO_OWNER = "Preyas552"
REPO_NAME = "LGT-Android-Roms"

SUPPORTED_DEVICES = {"coral", "taimen"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Update LineageOS OTA JSON metadata for a device."
    )
    parser.add_argument("--device", required=True, choices=sorted(SUPPORTED_DEVICES),
                        help="Device codename (coral or taimen)")
    parser.add_argument("--filename", required=True,
                        help="ROM zip filename")
    parser.add_argument("--size", required=True, type=int,
                        help="File size in bytes")
    parser.add_argument("--id", required=True,
                        help="Unique build ID/hash (e.g. SHA256)")
    parser.add_argument("--tag", required=True,
                        help="GitHub release tag (e.g. v1.0)")
    parser.add_argument("--datetime", dest="datetime_ts", type=int, default=None,
                        help="Unix timestamp (optional). If omitted, current UTC timestamp is used.")
    parser.add_argument("--version", default="20.0",
                        help="LineageOS version string (default: 20.0)")
    parser.add_argument("--romtype", default="unofficial",
                        help="ROM type (default: unofficial)")
    return parser.parse_args()


def validate_filename(device, filename):
    if device not in filename:
        raise ValueError(f"Filename '{filename}' does not contain device codename '{device}'")
    if not filename.endswith(".zip"):
        raise ValueError("Filename must end with .zip")


def build_url(tag, filename):
    return f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{tag}/{filename}"


def update_json_file(device, payload):
    ota_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(ota_dir, f"{device}.json")

    data = {"response": [payload]}

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    return json_path


def main():
    args = parse_args()

    try:
        validate_filename(args.device, args.filename)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    dt = args.datetime_ts or int(datetime.now(timezone.utc).timestamp())

    payload = {
        "datetime": dt,
        "filename": args.filename,
        "id": args.id,
        "romtype": args.romtype,
        "size": args.size,
        "url": build_url(args.tag, args.filename),
        "version": args.version
    }

    out_path = update_json_file(args.device, payload)
    print(f"Updated {out_path}")
    print(json.dumps({"response": [payload]}, indent=2))


if __name__ == "__main__":
    main()
