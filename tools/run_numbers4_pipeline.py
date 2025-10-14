import os
import subprocess
import sys
from importlib import import_module

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable or 'python'


def run(cmd, cwd=None):
    print(f"[run] {cmd}")
    res = subprocess.run(cmd, cwd=cwd or ROOT, shell=True)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def main():
    # 1) Scrape current month page and update CSV/SQLite
    scrape_py = os.path.join(ROOT, 'tools', 'scrape_numbers4_rakuten.py')
    if os.path.exists(scrape_py):
        run(f'"{PY}" "{scrape_py}"')
    else:
        print('[warn] scraper not found, skipping scrape step')

    # 2) Learn from latest draw if not yet learned
    upd_py = os.path.join(ROOT, 'tools', 'update_model_from_sqlite.py')
    if os.path.exists(upd_py):
        run(f'"{PY}" "{upd_py}"')
    else:
        print('[warn] updater not found, skipping learn step')

    # 3) Print predictions (advanced + model-based top-k)
    adv_py = os.path.join(ROOT, 'numbers4', 'advanced_predict_numbers4.py')
    if os.path.exists(adv_py):
        run(f'"{PY}" "{adv_py}"')
    else:
        print('[warn] advanced predictor not found')

    mdl_py = os.path.join(ROOT, 'numbers4', 'predict_numbers_with_model.py')
    if os.path.exists(mdl_py):
        run(f'"{PY}" "{mdl_py}"')
    else:
        print('[warn] model-based predictor not found')

    # 4) Basic predictor for reference
    basic_py = os.path.join(ROOT, 'numbers4', 'predict_numbers.py')
    if os.path.exists(basic_py):
        run(f'"{PY}" "{basic_py}"')


if __name__ == '__main__':
    main()
