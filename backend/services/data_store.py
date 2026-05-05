import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def read_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(filename: str, data):
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def read_regulation_text(reg_id: str):
    path = DATA_DIR / "texts" / f"{reg_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_regulation_text(reg_id: str, data):
    texts_dir = DATA_DIR / "texts"
    texts_dir.mkdir(parents=True, exist_ok=True)
    path = texts_dir / f"{reg_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def read_regulation_diagrams(reg_id: str):
    path = DATA_DIR / "diagrams" / f"{reg_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_regulation_diagrams(reg_id: str, data):
    diagrams_dir = DATA_DIR / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    path = diagrams_dir / f"{reg_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def list_regulations():
    data = read_json("regulations.json")
    if not data:
        return []
    return [r for r in data if r.get("id") and r["id"] != "制度序号" and r.get("name") != "制度名称"]


def list_authority():
    data = read_json("authority.json")
    if not data:
        return []
    return data


def get_authority_mapping():
    data = read_json("authority_mapping.json")
    if not data:
        return {}
    return data


def get_config():
    import os
    regs = list_regulations()
    auths = list_authority()
    texts_dir = DATA_DIR / "texts"
    diagrams_dir = DATA_DIR / "diagrams"
    texts_count = len([f for f in texts_dir.glob("*.json")]) if texts_dir.exists() else 0
    diagrams_count = len([f for f in diagrams_dir.glob("*.json")]) if diagrams_dir.exists() else 0

    last_modified = None
    for f in [DATA_DIR / "regulations.json", DATA_DIR / "authority.json"]:
        if f.exists():
            mtime = f.stat().st_mtime
            from datetime import datetime, timezone
            ts = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
            if last_modified is None or ts > last_modified:
                last_modified = ts

    return {
        "data_dir": str(DATA_DIR),
        "regulations_count": len(regs),
        "authority_count": len(auths),
        "texts_count": texts_count,
        "diagrams_count": diagrams_count,
        "last_modified": last_modified,
    }
