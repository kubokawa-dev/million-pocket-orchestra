import os
import psycopg2
from typing import Tuple
from dotenv import load_dotenv

import pandas as pd
import streamlit as st

from numbers4.predict_ensemble import generate_ensemble_prediction

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Numbers4 予測可視化", layout="wide")

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

# --- Loto6 テーブル自動作成（なければ作成） ---
def ensure_loto6_tables():
    con = get_db_connection()
    cur = con.cursor()
    # 抽選データテーブル
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loto6_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT,
            numbers TEXT
        )
    """)
    # 予測ログテーブル
    cur.execute("""
        CREATE TABLE IF NOT EXISTS loto6_predictions_log (
            id SERIAL PRIMARY KEY,
            created_at TEXT,
            source TEXT,
            label TEXT,
            number TEXT
        )
    """)
    con.commit()
    con.close()

# 起動時にテーブル存在確認・作成（ファイルの先頭で必ず実行）
ensure_loto6_tables()

@st.cache_data(show_spinner=False)
def load_draws(limit: int = 500) -> pd.DataFrame:
    con = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"""
            SELECT draw_number, draw_date, numbers
            FROM numbers4_draws
            ORDER BY draw_number DESC
            LIMIT {int(limit)}
            """,
            con,
        )
    finally:
        con.close()
    if df.empty:
        return df
    df = df.sort_values("draw_number").reset_index(drop=True)
    df["draw_date_dt"] = pd.to_datetime(df["draw_date"], errors="coerce", format='mixed')
    try:
        df["draw_date_dt"] = df["draw_date_dt"].dt.tz_localize(None)
    except Exception:
        pass
    df["numbers_str"] = df["numbers"].astype(str).str.zfill(4)
    return df

@st.cache_data(show_spinner=False)
def load_predictions() -> pd.DataFrame:
    con = get_db_connection()
    try:
        df = pd.read_sql_query(
            """
            SELECT id, created_at, source, label, number
            FROM numbers4_predictions_log
            ORDER BY created_at ASC, id ASC
            """,
            con,
        )
    finally:
        con.close()
    if df.empty:
        return df
    df["created_at_dt"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce").dt.tz_localize(None)
    df["predicted_number_str"] = df["number"].astype(str).str.zfill(4)
    return df

@st.cache_data(show_spinner=False)
def load_loto6_draws(limit: int = 500) -> pd.DataFrame:
    con = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"""
            SELECT draw_number, draw_date, numbers
            FROM loto6_draws
            ORDER BY draw_number DESC
            LIMIT {int(limit)}
            """,
            con,
        )
    finally:
        con.close()
    if df.empty:
        return df
    df = df.sort_values("draw_number").reset_index(drop=True)
    df["draw_date_dt"] = pd.to_datetime(df["draw_date"], errors="coerce", format='mixed')
    try:
        df["draw_date_dt"] = df["draw_date_dt"].dt.tz_localize(None)
    except Exception:
        pass
    df["numbers_str"] = df["numbers"].astype(str)
    return df

@st.cache_data(show_spinner=False)
def load_loto6_predictions() -> pd.DataFrame:
    con = get_db_connection()
    try:
        df = pd.read_sql_query(
            """
            SELECT id, created_at, source, label, number
            FROM loto6_predictions_log
            ORDER BY created_at ASC, id ASC
            """,
            con,
        )
    finally:
        con.close()
    if df.empty:
        return df
    df["created_at_dt"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce").dt.tz_localize(None)
    df["predicted_number_str"] = df["number"].astype(str)
    return df

def map_predictions_to_draws(draws_df: pd.DataFrame, preds_df: pd.DataFrame) -> pd.DataFrame:
    if draws_df.empty or preds_df.empty:
        return pd.DataFrame()
    # asof-map each prediction to the next draw at/after created_at
    mapped = pd.merge_asof(
        preds_df.sort_values("created_at_dt"),
        draws_df[["draw_number", "draw_date_dt", "numbers_str"]].sort_values("draw_date_dt"),
        left_on="created_at_dt",
        right_on="draw_date_dt",
        direction="forward",
    )
    mapped = mapped.dropna(subset=["draw_number"]).copy()
    if mapped.empty:
        return mapped
    mapped["draw_number"] = mapped["draw_number"].astype(int)
    return mapped

def compute_hits(mapped: pd.DataFrame) -> pd.DataFrame:
    if mapped.empty:
        return mapped
    # rank within draw by created_at (oldest first)
    mapped = mapped.sort_values(["draw_number", "created_at_dt", "id"]).copy()
    mapped["rank"] = mapped.groupby("draw_number").cumcount() + 1
    # hit types
    def hit_type_row(row) -> str:
        p = row["predicted_number_str"]
        a = row["numbers_str"]
        if p == a:
            return "straight"
        # box: same multiset
        from collections import Counter
        return "box" if Counter(p) == Counter(a) else "miss"

    mapped["hit_type"] = mapped.apply(hit_type_row, axis=1)
    # display-friendly model string
    mapped["model"] = mapped.apply(
        lambda r: (r["source"] or "unknown") + (f" / {r['label']}" if isinstance(r["label"], str) and r["label"] else ""),
        axis=1,
    )
    return mapped

def map_loto6_predictions_to_draws(draws_df: pd.DataFrame, preds_df: pd.DataFrame) -> pd.DataFrame:
    if draws_df.empty or preds_df.empty:
        return pd.DataFrame()
    mapped = pd.merge_asof(
        preds_df.sort_values("created_at_dt"),
        draws_df[["draw_number", "draw_date_dt", "numbers_str"]].sort_values("draw_date_dt"),
        left_on="created_at_dt",
        right_on="draw_date_dt",
        direction="forward",
    )
    mapped = mapped.dropna(subset=["draw_number"]).copy()
    if mapped.empty:
        return mapped
    mapped["draw_number"] = mapped["draw_number"].astype(int)
    return mapped

def compute_loto6_hits(mapped: pd.DataFrame) -> pd.DataFrame:
    if mapped.empty:
        return mapped
    mapped = mapped.sort_values(["draw_number", "created_at_dt", "id"]).copy()
    mapped["rank"] = mapped.groupby("draw_number").cumcount() + 1
    def hit_type_row(row) -> str:
        p = row["predicted_number_str"]
        a = row["numbers_str"]
        return "hit" if p == a else "miss"
    mapped["hit_type"] = mapped.apply(hit_type_row, axis=1)
    mapped["model"] = mapped.apply(
        lambda r: (r["source"] or "unknown") + (f" / {r['label']}" if isinstance(r["label"], str) and r["label"] else ""),
        axis=1,
    )
    return mapped

# Sidebar controls
st.sidebar.header("フィルター")
last_n = st.sidebar.slider("表示する直近回数", min_value=10, max_value=500, value=100, step=10)
sources_filter = st.sidebar.multiselect("ソース(source)", [])
label_query = st.sidebar.text_input("ラベルに含む文字列 (部分一致)", "")

# Load data
with st.spinner("データ読込中..."):
    draws_df = load_draws(limit=last_n)
    preds_df = load_predictions()
    mapped = map_predictions_to_draws(draws_df, preds_df)
    mapped = compute_hits(mapped)

# --- 回号フィルター追加 ---
draw_numbers_available = mapped["draw_number"].unique() if not mapped.empty else []
draw_number_filter = st.sidebar.selectbox(
    "回号で絞り込み (空欄は全件)",
    options=["(全件)"] + [str(n) for n in sorted(draw_numbers_available, reverse=True)],
    index=0
)

# Initialize dynamic filter options after data load
if not mapped.empty:
    all_sources = sorted(mapped["source"].dropna().unique().tolist())
    if not sources_filter:
        sources_filter = []  # default none -> treat as all

# Apply filters
filtered = mapped.copy()
if sources_filter:
    filtered = filtered[filtered["source"].isin(sources_filter)]
if label_query:
    filtered = filtered[filtered["label"].fillna("").str.contains(label_query, case=False, na=False)]
if draw_number_filter != "(全件)":
    filtered = filtered[filtered["draw_number"] == int(draw_number_filter)]

st.title("Numbers4 & Loto6 予測可視化 (Streamlit)")

# --- Tab UI ---
tabs = st.tabs(["ナンバーズ4", "ロト6"])

with tabs[0]:
    # --- ナンバーズ4タブ ---
    st.header("🔮 最新の当選番号を予測する (ナンバーズ4)")
    # Prediction Section
    if st.button("予測を実行"):
        st.info("アンサンブル予測を開始します。これには数分かかることがあります...")

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(p: float, msg: str):
            """Callback to update Streamlit progress bar."""
            progress_bar.progress(int(p * 100))
            status_text.text(msg)

        try:
            # Initialize status
            update_progress(0, "予測プロセスを開始しています...")
            
            prediction_df, _ = generate_ensemble_prediction(progress_callback=update_progress)
            
            update_progress(1.0, "予測が完了しました！")
            # Keep success message for a bit before clearing
            st.success("予測が完了しました！")
            progress_bar.empty()
            status_text.empty()

            st.subheader("予測結果")
            st.write(f"予測実行日時: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

            st.write("予測結果のカラム一覧:", list(prediction_df.columns))

            if prediction_df is not None and not prediction_df.empty:
                # Display results in a modern way
                num_predictions = len(prediction_df)
                cols = st.columns(num_predictions)
                # for i, row in prediction_df.iterrows():
                #     with cols[i]:
                #         st.metric(
                #             label=f"予測 {i+1}",
                #             value="(カラム名調査中)",
                #             help="(カラム名調査中)"
                #         )
                
                st.caption("詳細な予測の内訳:")
                st.dataframe(prediction_df, use_container_width=True)
            else:
                st.warning("予測結果を生成できませんでした。")

        except Exception as e:
            st.error(f"予測中にエラーが発生しました: {e}")
            st.exception(e) # show traceback

    st.divider()

    # KPIs
    st.header("📈 過去の予測パフォーマンス")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("対象回数", draws_df["draw_number"].nunique() if not draws_df.empty else 0)
    with col2:
        st.metric("予測件数", int(filtered.shape[0]))
    with col3:
        straight_hits = int((filtered["hit_type"] == "straight").sum()) if not filtered.empty else 0
        st.metric("ストレート的中", straight_hits)
    with col4:
        box_hits = int((filtered["hit_type"] == "box").sum()) if not filtered.empty else 0
        st.metric("ボックス的中", box_hits)

    # Per-draw table
    st.subheader("回ごとの予測一覧")
    if filtered.empty:
        st.info("表示できるデータがありません。フィルターを見直してください。")
    else:
        # Show most recent first
        to_show = filtered.sort_values(["draw_number", "rank"], ascending=[False, True])[
            [
                "draw_number",
                "numbers_str",
                "rank",
                "predicted_number_str",
                "hit_type",
                "model",
                "created_at",
            ]
        ]
        to_show = to_show.rename(
            columns={
                "numbers_str": "当選番号",
                "draw_number": "回",
                "predicted_number_str": "予測番号",
                "hit_type": "ヒット",
                "model": "モデル",
                "created_at": "作成時刻",
                "rank": "順位",
            }
        )
        st.dataframe(to_show, use_container_width=True, hide_index=True)

    # Aggregated hits per draw (chart)
    st.subheader("回ごとの的中数")
    if not filtered.empty:
        agg = (
            filtered.assign(hit=lambda d: d["hit_type"].isin(["straight", "box"]).astype(int))
            .groupby("draw_number")["hit"]
            .sum()
            .reset_index()
            .sort_values("draw_number")
        )
        agg = agg.rename(columns={"draw_number": "回", "hit": "的中数"})
        st.bar_chart(agg.set_index("回"))

    st.caption("データは PostgreSQL の numbers4_draws / numbers4_predictions_log を利用しています。created_at 以降で最初の抽選回に予測を割り当てて比較しています。")

with tabs[1]:
    # --- ロト6タブ ---
    st.header("🔮 最新の当選番号を予測する (ロト6)")

    # --- サイドバー ---
    st.sidebar.header("ロト6フィルター")
    last_n_loto6 = st.sidebar.slider("表示する直近回数 (ロト6)", min_value=10, max_value=500, value=100, step=10)
    # sources_filter_loto6 = st.sidebar.multiselect("ソース(source) (ロト6)", [])
    # label_query_loto6 = st.sidebar.text_input("ラベルに含む文字列 (ロト6)", "")

    # データロード
    with st.spinner("ロト6データ読込中..."):
        draws_df_loto6 = load_loto6_draws(limit=last_n_loto6)
        preds_df_loto6 = load_loto6_predictions()
        mapped_loto6 = map_loto6_predictions_to_draws(draws_df_loto6, preds_df_loto6)
        filtered_loto6 = compute_loto6_hits(mapped_loto6)

    def compute_loto6_hits(mapped: pd.DataFrame) -> pd.DataFrame:
        if mapped.empty:
            return mapped
        mapped = mapped.sort_values(["draw_number", "created_at_dt", "id"]).copy()
        mapped["rank"] = mapped.groupby("draw_number").cumcount() + 1
        def hit_type_row(row) -> str:
            p = row["predicted_number_str"]
            a = row["numbers_str"]
            return "hit" if p == a else "miss"
        mapped["hit_type"] = mapped.apply(hit_type_row, axis=1)
        mapped["model"] = mapped.apply(
            lambda r: (r["source"] or "unknown") + (f" / {r['label']}" if isinstance(r["label"], str) and r["label"] else ""),
            axis=1,
        )
        return mapped

    # --- サイドバー ---
    st.sidebar.header("ロト6フィルター")
    last_n_loto6 = st.sidebar.slider("表示する直近回数 (ロト6)", min_value=10, max_value=500, value=100, step=10)
    sources_filter_loto6 = st.sidebar.multiselect("ソース(source) (ロト6)", [])
    label_query_loto6 = st.sidebar.text_input("ラベルに含む文字列 (ロト6)", "")

    # データロード
    with st.spinner("ロト6データ読込中..."):
        draws_df_loto6 = load_loto6_draws(limit=last_n_loto6)
        preds_df_loto6 = load_loto6_predictions()
        mapped_loto6 = map_loto6_predictions_to_draws(draws_df_loto6, preds_df_loto6)
        mapped_loto6 = compute_loto6_hits(mapped_loto6)

    draw_numbers_available_loto6 = mapped_loto6["draw_number"].unique() if not mapped_loto6.empty else []
    draw_number_filter_loto6 = st.sidebar.selectbox(
        "回号で絞り込み (ロト6)",
        options=["(全件)"] + [str(n) for n in sorted(draw_numbers_available_loto6, reverse=True)],
        index=0
    )

    # フィルター適用
    filtered_loto6 = mapped_loto6.copy()
    if sources_filter_loto6:
        filtered_loto6 = filtered_loto6[filtered_loto6["source"].isin(sources_filter_loto6)]
    if label_query_loto6:
        filtered_loto6 = filtered_loto6[filtered_loto6["label"].fillna("").str.contains(label_query_loto6, case=False, na=False)]
    if draw_number_filter_loto6 != "(全件)":
        filtered_loto6 = filtered_loto6[filtered_loto6["draw_number"] == int(draw_number_filter_loto6)]

    # --- 予測ボタン ---
    st.subheader("ロト6予測ボタン")
    if st.button("ロト6予測を実行"):
        from loto6.advanced_predict_loto6 import predict
        with st.spinner("ロト6予測を計算中..."):
            try:
                result = predict()
                st.write(result)  # デバッグ用: 予測結果の中身を表示
                if not result or not all(k in result for k in ["hot", "balanced", "overdue", "pair"]):
                    st.warning("予測結果がありませんでした。CSVファイルやロジックをご確認ください。")
                else:
                    st.success("予測が完了しました！")
                    st.subheader("予測結果一覧")
                    labels = ["頻出/ホット", "バランス", "未出現/オーバーデュ", "ペア相性"]
                    keys = ["hot", "balanced", "overdue", "pair"]
                    df_result = pd.DataFrame({
                        "視点": labels,
                        "予測番号": [' '.join(f"{n:02d}" for n in result[k]) for k in keys],
                        "補足": [f"{labels[i]}視点の予測セット" for i in range(4)]
                    })
                    st.dataframe(df_result, use_container_width=True, hide_index=True)
                    st.caption(f"偶奇バランスTop: {result.get('eo_summary','-')}")
                    if 'sum_range' in result:
                        smin, smax, mu = result['sum_range']
                        st.caption(f"合計値レンジ: {smin}〜{smax} (平均≈{mu:.1f})")
            except Exception as e:
                st.error(f"ロト6予測中にエラーが発生しました: {e}")
                st.exception(e)

    st.divider()

    # --- KPIs ---
    st.header("📈 過去の予測パフォーマンス (ロト6)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("対象回数", draws_df_loto6["draw_number"].nunique() if not draws_df_loto6.empty else 0)
    with col2:
        st.metric("予測件数", int(filtered_loto6.shape[0]))
    with col3:
        hits = int((filtered_loto6["hit_type"] == "hit").sum()) if not filtered_loto6.empty else 0
        st.metric("的中数", hits)

    # --- テーブル ---
    st.subheader("回ごとの予測一覧 (ロト6)")
    if filtered_loto6.empty:
        st.info("表示できるデータがありません。フィルターを見直してください。")
    else:
        to_show_loto6 = filtered_loto6.sort_values(["draw_number", "rank"], ascending=[False, True])[
            [
                "draw_number",
                "numbers_str",
                "rank",
                "predicted_number_str",
                "hit_type",
                "model",
                "created_at",
            ]
        ]
        to_show_loto6 = to_show_loto6.rename(
            columns={
                "numbers_str": "当選番号",
                "draw_number": "回",
                "predicted_number_str": "予測番号",
                "hit_type": "ヒット",
                "model": "モデル",
                "created_at": "作成時刻",
                "rank": "順位",
            }
        )
        st.dataframe(to_show_loto6, use_container_width=True, hide_index=True)

    # --- グラフ ---
    st.subheader("回ごとの的中数 (ロト6)")
    if not filtered_loto6.empty:
        agg_loto6 = (
            filtered_loto6.assign(hit=lambda d: d["hit_type"] == "hit")
            .groupby("draw_number")["hit"]
            .sum()
            .reset_index()
            .sort_values("draw_number")
        )
        agg_loto6 = agg_loto6.rename(columns={"draw_number": "回", "hit": "的中数"})
        st.bar_chart(agg_loto6.set_index("回"))

    st.caption("データは PostgreSQL の loto6_draws / loto6_predictions_log を利用しています。created_at 以降で最初の抽選回に予測を割り当てて比較しています。")
