#!/usr/bin/env python3
"""Entrypoint for the news-image-20261127 make.fun entry.

The repository ships the finished front page as entry.png (rendered at build
time). This program only copies that file to the output directory, checks it
is a whole PNG, and checks its sha256 against the value recorded below. It
uses the standard library only, reads nothing from the network, and always
writes the same bytes.
"""

import hashlib
import os
import sys

EXPECTED_SHA256 = "51a51d2c0e8ff3be1fa510cb51d19f44db15ce4c0cde1eee0a86e67978406ad4"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    with open(source, "rb") as handle:
        payload = handle.read()

    if payload[:8] != PNG_SIGNATURE:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        print("entry.png sha256 mismatch: got %s" % digest, file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(payload)
    # Confirm the copy on disk matches the verified bytes exactly.
    with open(target, "rb") as handle:
        copied = handle.read()
    if hashlib.sha256(copied).hexdigest() != EXPECTED_SHA256:
        print("written entry.png failed its sha256 check", file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, sha256 %s)" % (target, len(payload), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
