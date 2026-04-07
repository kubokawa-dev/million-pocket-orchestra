---
description: 予測結果を実際の当選番号で更新します
args:
  - name: prediction_id
    description: 予測ID（数値）
    required: true
  - name: actual_numbers
    description: 実際の当選番号（4桁）
    required: true
---

```bash
python numbers4/manage_prediction_history.py update ${prediction_id} ${actual_numbers}
```










