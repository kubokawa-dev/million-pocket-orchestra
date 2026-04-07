import os
import psycopg2
import pandas as pd
import streamlit as st
import subprocess
import sys
from typing import Tuple
from dotenv import load_dotenv

# Import prediction logic
from numbers4.predict_ensemble import generate_ensemble_prediction, generate_similar_patterns_n4
from loto6.ultimate_predict_ensemble import run_ultimate_loto6_prediction

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or 'python'

st.set_page_config(
    page_title="Takarakuji AI — Numbers4 / Loto6 prediction (宝くじAI)",
    page_icon="🎰",
    layout="wide",
)

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

# --- Database Helper Functions ---
@st.cache_data(show_spinner=False)
def load_n4_draws(limit: int = 100) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT draw_number, draw_date, numbers FROM numbers4_draws ORDER BY draw_number DESC LIMIT {limit}",
            conn
        )
    finally:
        conn.close()
    if not df.empty:
        df["draw_date_dt"] = pd.to_datetime(df["draw_date"], errors="coerce")
        df["numbers_str"] = df["numbers"].astype(str).str.zfill(4)
        
        # Split numbers into d1, d2, d3, d4 for pattern analysis
        # Assuming numbers column is like "1234"
        df['d1'] = df['numbers'].astype(str).str[0].astype(int)
        df['d2'] = df['numbers'].astype(str).str[1].astype(int)
        df['d3'] = df['numbers'].astype(str).str[2].astype(int)
        df['d4'] = df['numbers'].astype(str).str[3].astype(int)
        
        # Sort ascending for pattern analysis (which often uses .tail())
        df = df.sort_values("draw_number", ascending=True).reset_index(drop=True)
        
    return df

@st.cache_data(show_spinner=False)
def load_loto6_draws(limit: int = 100) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT draw_number, draw_date, numbers, bonus_number FROM loto6_draws ORDER BY draw_number DESC LIMIT {limit}",
            conn
        )
    finally:
        conn.close()
    if not df.empty:
        df["draw_date_dt"] = pd.to_datetime(df["draw_date"], errors="coerce")
        df["numbers_str"] = df["numbers"].astype(str)
    return df

@st.cache_data(show_spinner=False)
def load_n4_predictions(limit: int = 500) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT id, created_at, source, label, number FROM numbers4_predictions_log ORDER BY id DESC LIMIT {limit}",
            conn
        )
    finally:
        conn.close()
    if not df.empty:
        df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce").dt.tz_localize(None)
        df["predicted_number_str"] = df["number"].astype(str).str.zfill(4)
    return df

@st.cache_data(show_spinner=False)
def load_loto6_predictions(limit: int = 500) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT id, created_at, source, label, number FROM loto6_predictions_log ORDER BY id DESC LIMIT {limit}",
            conn
        )
    finally:
        conn.close()
    if not df.empty:
        df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce").dt.tz_localize(None)
        df["predicted_number_str"] = df["number"].astype(str)
    return df

# --- UI Components ---

st.title("💰 宝くじAI: AI Lottery Prediction")
st.markdown("### ナンバーズ4 & ロト6 最強予測システム (v10.0 / Ultimate)")

tabs = st.tabs(["🔢 Numbers 4", "🎱 Loto 6", "📊 History & Stats"])

# === NUMBERS 4 TAB ===
with tabs[0]:
    st.header("Numbers 4 Prediction")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. データの更新")
        if st.button("最新データを取得＆学習 (Scrape & Learn)"):
            with st.status("データ更新プロセスを実行中...", expanded=True) as status:
                st.write("Fetching latest data from Rakuten...")
                # Run scraper
                scrape_script = os.path.join(ROOT_DIR, 'tools', 'scrape_numbers4_rakuten.py')
                try:
                    res = subprocess.run([PY, scrape_script], capture_output=True, text=True)
                    st.code(res.stdout)
                    if res.returncode == 0:
                        st.write("✅ Scraping completed.")
                    else:
                        st.error("Scraping failed.")
                except Exception as e:
                    st.error(f"Error running scraper: {e}")

                st.write("Running internal model learning...")
                # Run learning (via update_learning_models logic essentially)
                # We can call the pipeline script's learning function or just call learn_from_predictions.py
                # For simplicity, let's call the learn script directly if we can fetch the latest number
                # Actually, the pipeline script is safer.
                pipeline_script = os.path.join(ROOT_DIR, 'tools', 'run_numbers4_pipeline.py')
                # But pipeline runs prediction too. Let's just rely on the user clicking "Predict" separately for better UI control.
                # Just run scrape is enough? No, online learning needs to run.
                # Let's run the full pipeline script in background? No, users want immediate feedback.
                
                # Let's manually trigger learning
                try:
                    # Get latest number from DB
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT numbers FROM numbers4_draws ORDER BY draw_date DESC LIMIT 1")
                    row = cur.fetchone()
                    conn.close()
                    
                    if row:
                        latest_num = row[0]
                        st.write(f"Latest Number: {latest_num}")
                        learn_script = os.path.join(ROOT_DIR, 'numbers4', 'learn_from_predictions.py')
                        res_learn = subprocess.run([PY, learn_script, latest_num], capture_output=True, text=True)
                        st.code(res_learn.stdout)
                        st.write("✅ Learning completed.")
                    else:
                        st.warning("No data found to learn from.")
                        
                except Exception as e:
                    st.error(f"Error during learning: {e}")
                
                status.update(label="データ更新完了！", state="complete", expanded=False)

    with col2:
        st.subheader("2. AI予測の実行")
        if st.button("アンサンブル予測を実行 (Predict)"):
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            def update_progress(p, msg):
                progress_bar.progress(int(p * 100))
                status_text.text(f"{int(p*100)}% - {msg}")
            
            try:
                # Run prediction in-process
                pred_df, weights = generate_ensemble_prediction(progress_callback=update_progress)
                
                status_text.text("予測完了！")
                progress_bar.progress(100)
                st.balloons()
                
                st.success(f"予測が完了しました！ (Top {len(pred_df)} candidates)")
                
                # Show Top 10 with details
                st.subheader("🏆 Top 10 Predictions")
                
                # Prepare data for display
                top_10 = pred_df.head(10).copy()
                top_10.index = range(1, 11)
                st.dataframe(top_10, use_container_width=True)
                
                st.write("---")
                st.subheader("💡 類似パターン提案 (Top 3)")
                
                # Load draws for pattern analysis
                all_draws = load_n4_draws(limit=1000)
                
                for i, row in top_10.head(3).iterrows():
                    pred_num = row['prediction']
                    score = row['score']
                    st.markdown(f"**第{i}位: `{pred_num}` (Score: {score:.1f})**")
                    
                    patterns = generate_similar_patterns_n4(pred_num, count=3, all_draws_df=all_draws)
                    if patterns:
                        for p_num, p_desc in patterns:
                            st.text(f"  ↳ {p_num} : {p_desc}")
                    else:
                        st.text("  (No similar patterns found)")
                    st.write("")
                    
                st.expander("モデルの重み (Weights)").json(weights)
                
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                import traceback
                st.text(traceback.format_exc())

# === LOTO 6 TAB ===
with tabs[1]:
    st.header("Loto 6 Prediction")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. データの更新")
        if st.button("最新データを取得＆学習 (Loto6)"):
            with st.status("データ更新プロセスを実行中...", expanded=True) as status:
                st.write("Fetching latest data from Rakuten...")
                scrape_script = os.path.join(ROOT_DIR, 'tools', 'scrape_loto6_rakuten.py')
                try:
                    res = subprocess.run([PY, scrape_script], capture_output=True, text=True)
                    st.code(res.stdout)
                    st.write("✅ Scraping completed.")
                except Exception as e:
                    st.error(f"Error running scraper: {e}")

                st.write("Running internal model learning...")
                try:
                    # Get latest number from DB
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT numbers, bonus_number, draw_number FROM loto6_draws ORDER BY draw_date DESC LIMIT 1")
                    row = cur.fetchone()
                    conn.close()
                    
                    if row:
                        nums_str = row[0] # "01,02,..."
                        bonus = str(row[1])
                        draw_n = str(row[2])
                        nums_clean = nums_str.replace(',', '').replace(' ', '')
                        
                        st.write(f"Latest: {nums_str} (Bonus: {bonus})")
                        
                        learn_script = os.path.join(ROOT_DIR, 'loto6', 'learn_from_predictions.py')
                        cmd = [PY, learn_script, nums_clean, bonus, draw_n]
                        res_learn = subprocess.run(cmd, capture_output=True, text=True)
                        st.code(res_learn.stdout)
                        st.write("✅ Learning completed.")
                    else:
                        st.warning("No data found.")
                        
                except Exception as e:
                    st.error(f"Error during learning: {e}")
                
                status.update(label="データ更新完了！", state="complete", expanded=False)

    with col2:
        st.subheader("2. AI予測の実行")
        if st.button("アンサンブル予測を実行 (Loto6 Predict)"):
            with st.spinner("10+個のモデルで計算中... (LightGBM含む)"):
                try:
                    # Capture stdout to show logs?
                    # run_ultimate_loto6_prediction prints a lot.
                    # We can't easily capture print output in Streamlit unless we redirect stdout.
                    # For now just run it.
                    
                    df_res = run_ultimate_loto6_prediction(top_n=50)
                    
                    if df_res is not None and not df_res.empty:
                        st.balloons()
                        st.success(f"予測完了！ (Candidates: {len(df_res)})")
                        
                        st.subheader("🏆 Top Predictions")
                        
                        # Add stars column for display
                        def get_stars(score):
                            if score >= 5.0: return "★★★★★"
                            if score >= 4.0: return "★★★★☆"
                            if score >= 3.0: return "★★★☆☆"
                            if score >= 2.0: return "★★☆☆☆"
                            return "★☆☆☆☆"
                        
                        df_display = df_res.copy()
                        df_display['Recommends'] = df_display['score'].apply(get_stars)
                        # Reorder
                        cols = ['Recommends', 'score', 'numbers']
                        df_display = df_display[cols]
                        
                        st.dataframe(df_display.head(20), use_container_width=True)
                        
                        st.caption("※ 上位の組み合わせほど、複数のモデル（統計＋AI）が強く推奨しています。")
                        
                    else:
                        st.error("予測結果が空でした。")
                        
                except Exception as e:
                    st.error(f"Loto6 Prediction Error: {e}")
                    import traceback
                    st.text(traceback.format_exc())

# === HISTORY TAB ===
with tabs[2]:
    st.header("予測履歴と当選確認")
    
    st.subheader("🔥 Hot Model トレンド (直近50回)")
    st.write("過去50回でどのモデルが一番強かったかを分析します！")
    
    if st.button("トレンドを分析する！"):
        with st.spinner("過去50回分のデータを分析中...✨"):
            try:
                from numbers4.predict_hot_models import analyze_hot_models
                # 最新の回を取得
                df_n4 = load_n4_draws(limit=1)
                if not df_n4.empty:
                    latest_draw = int(df_n4.iloc[0]['draw_number'])
                    target_draw = latest_draw + 1
                    
                    hot_models = analyze_hot_models(target_draw, lookback=50, top_k=100, quiet=True)
                    
                    if hot_models:
                        # データフレームに変換して表示
                        import pandas as pd
                        trend_df = pd.DataFrame(hot_models, columns=["モデル名", "トレンドスコア"])
                        trend_df.index = range(1, len(trend_df) + 1)
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.dataframe(trend_df, use_container_width=True)
                        
                        with col2:
                            top_model = hot_models[0][0]
                            st.success(f"💖 今一番キテるのは【{top_model}】だよ！")
                            st.info("※ このスコアは毎回の予測時に自動で計算されて、上位モデルにはボーナスポイントが加算されるよ！")
                            
                            # 棒グラフで可視化
                            st.bar_chart(trend_df.set_index("モデル名"))
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                
    st.divider()
    
    st.subheader("Numbers 4 最新データ")
    df_n4 = load_n4_draws()
    st.dataframe(df_n4, use_container_width=True)
    
    st.divider()
    
    st.subheader("Loto 6 最新データ")
    df_l6 = load_loto6_draws()
    st.dataframe(df_l6, use_container_width=True)
    
    # Simple Hit Check Logic could be added here similar to previous app
    # For now, just showing raw data is a good start.

st.sidebar.info("Developed by Kubocchi 宝くじAI Project")
