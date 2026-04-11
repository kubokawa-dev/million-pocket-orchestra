from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional


def get_predictions_dir() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    predictions_dir = os.path.join(project_root, "predictions", "daily")
    os.makedirs(predictions_dir, exist_ok=True)
    return predictions_dir


def load_predictions_by_draw(draw_number: int) -> Optional[Dict]:
    pdir = get_predictions_dir()
    file_path = os.path.join(pdir, f"numbers3_{draw_number}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_daily_predictions(date_str: Optional[str] = None) -> Optional[Dict]:
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    pdir = get_predictions_dir()
    files = [
        fn
        for fn in os.listdir(pdir)
        if fn.startswith("numbers3_") and fn.endswith(".json")
    ]
    files.sort(reverse=True)
    for fn in files:
        fp = os.path.join(pdir, fn)
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == date_str:
            return data
    return None
