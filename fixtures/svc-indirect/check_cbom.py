"""Validate a CycloneDX-style CBOM for the svc-indirect fixture."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "cbom.json")
if not os.path.exists(path):
    raise SystemExit("cbom.json was not produced")
doc = json.load(open(path, encoding="utf-8"))

if doc.get("bomFormat") != "CycloneDX":
    raise SystemExit("bomFormat must be CycloneDX")
if not doc.get("specVersion"):
    raise SystemExit("specVersion is required")

components = doc.get("components")
if not isinstance(components, list) or not components:
    raise SystemExit("components must be a non-empty list")

names = []
for i, c in enumerate(components):
    if not isinstance(c, dict):
        raise SystemExit(f"component {i} is not an object")
    cp = c.get("cryptoProperties")
    if not isinstance(cp, dict):
        raise SystemExit(f"component {i} missing cryptoProperties")
    if not cp.get("assetType"):
        raise SystemExit(f"component {i} missing cryptoProperties.assetType")
    names.append(str(c.get("name", "")).lower())

blob = " ".join(names)
for needed in ("md5", "rsa"):
    if needed not in blob:
        raise SystemExit(f"missing cryptographic asset: {needed}")

print(f"CBOM OK ({len(components)} components)")
