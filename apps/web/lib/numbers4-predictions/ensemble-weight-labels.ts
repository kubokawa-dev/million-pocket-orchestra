/**
 * predict_ensemble.py の default_weights コメントと整合する表示名。
 * 未知のキーはラベル無しで英語キーのみ。
 */
const LABELS: Record<string, string> = {
  box_model: "ボックス特化型モデル",
  ml_neighborhood: "ML近傍探索",
  even_odd_pattern: "偶数/奇数パターン",
  low_sum_specialist: "低合計値特化",
  sequential_pattern: "連続数字パターン",
  adjacent_digit: "隣接数字パターン",
  cold_revival: "コールドナンバー復活",
  hot_pair: "ホットペア組み合わせ",
  box_pattern: "ボックスパターン分析",
  digit_freq_box: "数字頻度ボックス",
  state_chain: "model_state チェーン",
  transition_probability: "遷移確率",
  global_frequency: "全体頻度",
  digit_repetition: "数字再出現",
  digit_continuation: "桁継続",
  realistic_frequency: "現実的頻度",
  large_change: "大変化",
  advanced_heuristics: "統計分析",
  exploratory: "探索的分析",
  extreme_patterns: "極端パターン",
  basic_stats: "基本統計",
  ml_model_new: "機械学習（新）",
  lightgbm: "LightGBM",
  lgbm_box: "ボックスレベル LightGBM",
  demo: "デモ",
};

export function getEnsembleWeightJaLabel(key: string): string | undefined {
  return LABELS[key];
}

/** プレーンテキスト用: `box_model(ボックス特化型モデル)` */
export function formatEnsembleWeightKey(key: string): string {
  const ja = LABELS[key];
  return ja != null && ja !== "" ? `${key}(${ja})` : key;
}
