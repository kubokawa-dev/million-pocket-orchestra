import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable or 'python'


def run(cmd, cwd=None):
    print(f"[run] {cmd}")
    res = subprocess.run(cmd, cwd=cwd or ROOT, shell=True)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def main():
    # 1) Scrape current & previous month for Loto6
    scrape_py = os.path.join(ROOT, 'tools', 'scrape_loto6_rakuten.py')
    if os.path.exists(scrape_py):
        run(f'"{PY}" "{scrape_py}"')
    else:
        print('[warn] Loto6 scraper not found')

    # 2) Learn from latest draw if state is behind
    upd = os.path.join(ROOT, 'tools', 'update_loto6_model_from_sqlite.py')
    if os.path.exists(upd):
        run(f'"{PY}" "{upd}"')

    # 3) Predictions
    adv = os.path.join(ROOT, 'loto6', 'advanced_predict_loto6.py')
    if os.path.exists(adv):
        run(f'"{PY}" "{adv}"')
    else:
        print('[warn] advanced Loto6 predictor not found')

    mdl = os.path.join(ROOT, 'loto6', 'predict_loto6_with_model.py')
    if os.path.exists(mdl):
        run(f'"{PY}" "{mdl}"')
    else:
        print('[warn] model-based Loto6 predictor not found')

    basic = os.path.join(ROOT, 'loto6', 'predict_loto6.py')
    if os.path.exists(basic):
        run(f'"{PY}" "{basic}"')


if __name__ == '__main__':
    main()
