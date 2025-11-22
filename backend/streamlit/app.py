"""
YouTubeチャンネル分析ダッシュボード
Streamlitアプリケーション
"""
import sys
import os
from typing import List, Optional
from pathlib import Path
from importlib.util import find_spec

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
from textwrap import dedent

# 環境変数の読み込み
# 1. backend/.env を優先（バックエンド専用）
# 2. ルート直下の .env.local をフォールバック（既存の設定と共有）
backend_env = Path(__file__).parent.parent / '.env'
root_env_local = Path(__file__).parent.parent.parent / '.env.local'

if backend_env.exists():
    load_dotenv(backend_env)
elif root_env_local.exists():
    load_dotenv(root_env_local)

# 親ディレクトリをパスに追加（backend/db/rds.pyをインポートするため）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from utils.data_processor import (
    get_channels,
    get_channel_by_id,
    get_channel_by_youtube_id,
    get_videos_with_stats,
    get_video_stats_history,
    process_heatmap_data,
    process_tag_performance,
    compute_cohort_performance,
    detect_growth_anomalies,
    compute_tag_combinations,
    compute_funnel_metrics,
    simulate_revenue,
    build_channel_comparison,
    generate_auto_insights,
    suggest_publish_slots,
)

HAS_STATSMODELS = find_spec("statsmodels") is not None

# ページ設定
st.set_page_config(
    page_title="YouTube分析ダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

GLOBAL_STYLES = dedent("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;600&display=swap');

    :root {
        --background: #f6f8fb;
        --foreground: #111827;
        --panel: rgba(255, 255, 255, 0.3);
        --panel-border: rgba(255, 255, 255, 0.45);
        --card-shadow: 0 12px 40px rgba(15, 23, 42, 0.15);
        --youtube-red: #ff1a1a;
        --accent: linear-gradient(135deg, rgba(255, 26, 26, 0.9) 0%, rgba(220, 20, 20, 0.9) 100%);
    }

    * {
        font-family: "Inter", "Noto Sans JP", system-ui, -apple-system, BlinkMacSystemFont,
            "Helvetica Neue", Arial, "Yu Gothic", "Hiragino Kaku Gothic ProN", sans-serif;
    }

    body {
        color: var(--foreground);
    }

    #root, .stApp {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--background);
        position: relative;
        min-height: 100dvh;
        padding: 0 0 3rem;
        z-index: 0;
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        z-index: -2;
    }

    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        inset: 0;
        background:
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(79, 172, 254, 0.3) 0%, transparent 50%);
        z-index: -1;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .block-container {
        padding: 4.5rem 2.5rem 2.5rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 3.5rem 1.25rem 1.5rem;
        }
    }

    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }

    [data-testid="stSidebar"] * {
        color: #1f2937 !important;
    }

    .glass-panel {
        background: var(--panel);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--panel-border);
        border-radius: 20px;
        padding: 1.75rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
    }

    .app-header {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .app-branding h1 {
        margin: 0.25rem 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: #0f172a;
    }

    .app-branding p {
        margin: 0;
        color: #475569;
        max-width: 520px;
    }

    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #fff;
        background-image: var(--accent);
        box-shadow: 0 10px 30px rgba(255, 26, 26, 0.35);
    }

    .header-actions {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }

    .header-actions a {
        text-decoration: none;
    }

    .header-actions .primary {
        background-image: var(--accent);
        color: #fff;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 25px rgba(255, 26, 26, 0.35);
    }

    .header-actions .secondary {
        background: rgba(255, 255, 255, 0.65);
        color: #1f2937;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }

    .header-actions .primary,
    .header-actions .secondary {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.55rem 1.15rem;
        border-radius: 14px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .header-actions .primary:hover,
    .header-actions .secondary:hover {
        transform: translateY(-2px);
    }

    .glass-control {
        background: rgba(255, 255, 255, 0.65);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.1);
    }

    .stSelectbox [data-baseweb="select"], 
    .stRadio [data-baseweb="radio"],
    .stMultiSelect [data-baseweb="select"],
    .stTextInput div[data-baseweb="input"],
    .stNumberInput div[data-baseweb="input"],
    .stTextArea textarea,
    .stDateInput div[data-baseweb="input"],
    .stTimeInput div[data-baseweb="input"] {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }

    .stTextArea textarea {
        color: #111827;
        padding: 0.9rem 1rem;
    }

    .stSelectbox [data-baseweb="select"] * {
        background: transparent;
        color: #1f2937 !important;
    }

    .stSelectbox input {
        border: none !important;
        box-shadow: none !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input {
        background: transparent !important;
        color: #111827 !important;
    }

    .stSelectbox svg {
        color: #1f2937;
    }

    .hero-eyebrow {
        font-size: 0.85rem;
        font-weight: 600;
        color: rgba(17, 24, 39, 0.65);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.5rem;
        text-shadow: 0 8px 24px rgba(15, 23, 42, 0.4);
    }

    .hero-description {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        line-height: 1.6;
        max-width: 720px;
    }

    .channel-header {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
    }

    .channel-info h2 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #111827;
    }

    .channel-info p {
        margin: 0.35rem 0 0;
        color: #4b5563;
    }

    .channel-meta {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .channel-meta span {
        border-radius: 9999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #374151;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
    }

    .metric-card {
        border-radius: 18px;
        padding: 1.25rem;
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.35);
        box-shadow: 0 8px 32px rgba(15, 23, 42, 0.12);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.2);
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #111827;
    }

    .metric-sub {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }

    .tab-card {
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.12);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.4);
        border-radius: 9999px;
        padding: 0.75rem 1.25rem;
        color: #374151;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.45);
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-image: var(--accent);
        color: white;
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 10px 25px rgba(255, 26, 26, 0.35);
    }

    .stat-block {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1.25rem;
    }

    .stat-pill {
        display: inline-flex;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        background: rgba(17, 24, 39, 0.04);
        color: #374151;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .stPlotlyChart {
        border-radius: 16px;
        overflow: hidden;
    }

    .glass-table {
        margin-top: 1.5rem;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.12);
    }
</style>
""")

st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)


def format_number(value: Optional[int]) -> str:
    if value in (None, "", "N/A"):
        return "N/A"
    return f"{int(value):,}"


def render_hero_section():
    st.markdown(
        """
        <section class="glass-panel" style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0.15));">
            <p class="hero-eyebrow">Insight Dashboard</p>
            <h1 class="hero-title">YouTube チャンネル解析ダッシュボード</h1>
            <p class="hero-description">
                フロントエンドと同じトーン&マナーでチャンネルの成長と動画パフォーマンスを一望できます。
                サイドバーからチャンネルを選択するかIDを入力して、ヒートマップや成長カーブなどの詳細な分析を行ってください。
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_app_header():
    st.markdown(
        """
        <header class="glass-panel app-header">
            <div class="app-branding">
                <span class="brand-pill">YouTube Dashboard</span>
                <h1>データ活用のためのストリーミング解析ビュー</h1>
                <p>
                    バックエンドに同期された最新データを、フロントエンドと同じ世界観で確認できます。
                    チャンネルの深掘りや指標分析はこのビューから行えます。
                </p>
            </div>
            <div class="header-actions">
                <a class="primary" href="http://localhost:3000/channels" target="_blank" rel="noreferrer">
                    フロントUIを開く
                </a>
                <a class="secondary" href="https://developers.google.com/youtube/v3" target="_blank" rel="noreferrer">
                    YouTube Data API
                </a>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_channel_header(channel: dict):
    st.markdown(
        f"""
        <section class="glass-panel channel-header">
            <div class="channel-info">
                <p class="hero-eyebrow">現在のチャンネル</p>
                <h2>📺 {channel.get('title', 'Untitled Channel')}</h2>
                <p>ID: {channel.get('youtube_channel_id', 'N/A')}</p>
            </div>
            <div class="channel-meta">
                <span>DB ID: {channel.get('id')}</span>
                <span>動画 {format_number(channel.get('video_count'))} 本</span>
                <span>総再生 {format_number(channel.get('view_count'))} 回</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(channel: dict):
    metrics = [
        {"label": "登録者数", "value": format_number(channel.get("subscriber_count")), "sub": "Subscribers"},
        {"label": "総再生数", "value": format_number(channel.get("view_count")), "sub": "Total Views"},
        {"label": "動画数", "value": format_number(channel.get("video_count")), "sub": "Videos"},
        {"label": "チャンネルID", "value": channel.get("youtube_channel_id", "N/A"), "sub": "YouTube Channel"},
    ]
    st.markdown('<section class="glass-panel">', unsafe_allow_html=True)
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        col.markdown(
            f"""
            <article class="metric-card">
                <p class="metric-label">{metric["label"]}</p>
                <p class="metric-value">{metric["value"]}</p>
                <p class="metric-sub">{metric["sub"]}</p>
            </article>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</section>", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # 5分間キャッシュ
def load_channels():
    """チャンネル一覧をキャッシュ付きで読み込み"""
    try:
        return get_channels()
    except Exception as e:
        st.error(f"チャンネル一覧の取得に失敗しました: {str(e)}")
        return []


@st.cache_data(ttl=60)  # 1分間キャッシュ
def load_videos(channel_id: int):
    """動画データをキャッシュ付きで読み込み"""
    try:
        return get_videos_with_stats(channel_id)
    except Exception as e:
        st.error(f"動画データの取得に失敗しました: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=60)  # 1分間キャッシュ
def load_video_history(video_ids: List[int], days: int = 30):
    """動画の統計履歴をキャッシュ付きで読み込み"""
    try:
        return get_video_stats_history(video_ids, days)
    except Exception as e:
        st.error(f"統計履歴の取得に失敗しました: {str(e)}")
        return pd.DataFrame()


def main():
    render_app_header()
    render_hero_section()
    
    # サイドバー: チャンネル選択
    st.sidebar.header("チャンネル選択")
    
    channels = load_channels()
    
    if not channels:
        st.warning("登録されているチャンネルがありません。")
        st.info("まず、フロントエンドからチャンネルを登録してください。")
        return
    
    # チャンネル選択方法
    selection_method = st.sidebar.radio(
        "選択方法",
        ["一覧から選択", "YouTubeチャンネルIDで検索"]
    )
    
    selected_channel = None
    
    if selection_method == "一覧から選択":
        channel_options = {f"{ch['title']} (ID: {ch['id']})": ch['id'] for ch in channels}
        selected_channel_name = st.sidebar.selectbox(
            "チャンネルを選択",
            options=list(channel_options.keys())
        )
        if selected_channel_name:
            selected_channel_id = channel_options[selected_channel_name]
            selected_channel = get_channel_by_id(selected_channel_id)
    else:
        youtube_channel_id = st.sidebar.text_input(
            "YouTubeチャンネルIDを入力",
            placeholder="UCxxxxx または @channelname"
        )
        if youtube_channel_id:
            # @ハンドルの場合は@を削除
            if youtube_channel_id.startswith('@'):
                youtube_channel_id = youtube_channel_id[1:]
            
            selected_channel = get_channel_by_youtube_id(youtube_channel_id)
            if not selected_channel:
                st.sidebar.error("指定されたチャンネルが見つかりませんでした。")
    
    if not selected_channel:
        st.info("サイドバーからチャンネルを選択してください。")
        return
    
    # チャンネル情報の表示
    render_channel_header(selected_channel)
    render_metric_cards(selected_channel)
    
    # 動画データの取得
    videos_df = load_videos(selected_channel['id'])
    
    if videos_df.empty:
        st.warning("このチャンネルには動画が登録されていません。")
        return
    
    # 指標選択
    st.sidebar.header("分析設定")
    metric_options = {
        "再生数": "view_count",
        "いいね数": "like_count",
        "コメント数": "comment_count"
    }
    selected_metric_label = st.sidebar.selectbox(
        "分析指標",
        options=list(metric_options.keys())
    )
    selected_metric = metric_options[selected_metric_label]
    
    heatmap_df = process_heatmap_data(videos_df, selected_metric)
    tag_performance_df = process_tag_performance(videos_df, selected_metric)
    history_full_df = load_video_history(videos_df['id'].tolist(), days=120) if not videos_df.empty else pd.DataFrame()
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 曜日×時間帯ヒートマップ",
        "📊 動画長さ vs パフォーマンス",
        "📉 成長カーブ比較",
        "🏷️ タグ別パフォーマンス"
    ])
    
    # タブ1: 曜日×時間帯ヒートマップ
    with tab1:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader(f"曜日 × 時間帯ヒートマップ（{selected_metric_label}）")
        st.caption(f"動画の公開日時（曜日と時間帯）と{selected_metric_label}の関係を可視化")
        
        if not videos_df.empty and not heatmap_df.empty:
            fig = px.imshow(
                heatmap_df,
                labels=dict(x="時間帯（時）", y="曜日", color=selected_metric_label),
                x=[f"{hour}時" for hour in heatmap_df.columns],
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title=f"曜日 × 時間帯別の平均{selected_metric_label}"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # 統計情報
            st.subheader("統計情報")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最高値", f"{heatmap_df.max().max():,.0f}")
            with col2:
                st.metric("最低値", f"{heatmap_df.min().min():,.0f}")
            with col3:
                st.metric("平均値", f"{heatmap_df.mean().mean():,.0f}")
        else:
            st.info("ヒートマップデータがありません。")
        st.markdown('</section>', unsafe_allow_html=True)
    
    # タブ2: 動画長さ vs パフォーマンス
    with tab2:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader(f"動画長さ vs {selected_metric_label}")
        st.caption(f"動画の長さと{selected_metric_label}の関係を可視化")
        
        if not videos_df.empty:
            # 動画長さを分に変換
            videos_df['duration_min'] = videos_df['duration_sec'] / 60
            
            fig = px.scatter(
                videos_df,
                x='duration_min',
                y=selected_metric,
                hover_data=['title', 'published_at'],
                labels={
                    'duration_min': '動画長さ（分）',
                    selected_metric: selected_metric_label,
                    'title': 'タイトル',
                    'published_at': '公開日'
                },
                title=f"動画長さ vs {selected_metric_label}",
                trendline="ols" if HAS_STATSMODELS else None
            )
            fig.update_traces(
                marker=dict(size=8, opacity=0.6),
                hovertemplate='<b>%{hovertext}</b><br>' +
                            '動画長さ: %{x:.1f}分<br>' +
                            f'{selected_metric_label}: %{{y:,}}<br>' +
                            '<extra></extra>',
                hovertext=videos_df['title']
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            if not HAS_STATSMODELS:
                st.caption("回帰直線を表示するには backend/streamlit 環境で `pip install statsmodels` を実行してください。")
            
            # 統計情報
            st.subheader("統計情報")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("平均動画長さ", f"{videos_df['duration_min'].mean():.1f}分")
            with col2:
                st.metric(f"平均{selected_metric_label}", f"{videos_df[selected_metric].mean():,.0f}")
            with col3:
                correlation = videos_df['duration_min'].corr(videos_df[selected_metric])
                st.metric("相関係数", f"{correlation:.3f}")
        else:
            st.warning("動画データがありません。")
        st.markdown('</section>', unsafe_allow_html=True)
    
    # タブ3: 成長カーブ比較
    with tab3:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader(f"公開から30日間の成長カーブ比較（{selected_metric_label}）")
        st.caption("複数の動画の成長カーブを比較")
        
        if not videos_df.empty:
            # 動画選択
            video_options = {
                f"{row['title'][:50]}... (ID: {row['id']})" if len(row['title']) > 50 else f"{row['title']} (ID: {row['id']})": row['id']
                for _, row in videos_df.iterrows()
            }
            selected_video_ids = st.multiselect(
                "比較する動画を選択（複数選択可）",
                options=list(video_options.keys()),
                default=list(video_options.keys())[:5] if len(video_options) > 5 else list(video_options.keys())
            )
            
            if selected_video_ids:
                video_ids = [video_options[v] for v in selected_video_ids]
                history_df = load_video_history(video_ids, days=30)
                
                if not history_df.empty:
                    fig = go.Figure()
                    
                    for video_id in video_ids:
                        video_history = history_df[history_df['video_id'] == video_id]
                        if not video_history.empty:
                            video_title = video_history.iloc[0]['title']
                            fig.add_trace(go.Scatter(
                                x=video_history['days_since_publish'],
                                y=video_history[selected_metric],
                                mode='lines+markers',
                                name=video_title[:50] + '...' if len(video_title) > 50 else video_title,
                                hovertemplate='<b>%{fullData.name}</b><br>' +
                                            '公開から%{x}日目<br>' +
                                            f'{selected_metric_label}: %{{y:,}}<br>' +
                                            '<extra></extra>'
                            ))
                    
                    fig.update_layout(
                        title=f"公開から30日間の{selected_metric_label}推移",
                        xaxis_title="公開からの日数",
                        yaxis_title=selected_metric_label,
                        height=600,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("選択した動画の統計履歴データがありません。")
            else:
                st.info("比較する動画を選択してください。")
        else:
            st.warning("動画データがありません。")
        st.markdown('</section>', unsafe_allow_html=True)
    
    # タブ4: タグ別パフォーマンス
    with tab4:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader(f"タグ別の平均{selected_metric_label}")
        st.caption("タグごとの平均パフォーマンスを可視化")
        
        if not videos_df.empty and not tag_performance_df.empty:
            # トップ20を表示
            top_tags = tag_performance_df.head(20)
            
            fig = px.bar(
                top_tags,
                x=selected_metric,
                y='tag',
                orientation='h',
                labels={
                    selected_metric: selected_metric_label,
                    'tag': 'タグ'
                },
                title=f"タグ別の平均{selected_metric_label}（トップ20）"
            )
            fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # データテーブル
            st.subheader("データテーブル")
            st.markdown('<div class="glass-table">', unsafe_allow_html=True)
            st.dataframe(
                tag_performance_df.head(50),
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("タグデータがありません。")
        st.markdown('</section>', unsafe_allow_html=True)

    advanced_tabs = st.tabs([
        "📚 コホート分析",
        "⚡ 成長率と異常検知",
        "🔗 タグ組み合わせ",
        "🔁 ファネル / リテンション",
        "💰 収益シミュレーション",
        "🆚 チャンネル比較",
        "🧠 自動インサイト",
        "🗓️ 配信タイミング提案",
    ])
    
    (
        cohort_tab,
        anomaly_tab,
        combo_tab,
        funnel_tab,
        revenue_tab,
        compare_tab,
        insight_tab,
        schedule_tab,
    ) = advanced_tabs
    
    with cohort_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("公開月コホート別の指標推移")
        st.caption("公開月ごとの動画群が、公開後30日/90日でどう成長するかを可視化")
        
        if history_full_df.empty:
            st.info("コホート分析に必要な統計履歴データが不足しています。")
        else:
            cohort_df = compute_cohort_performance(history_full_df, selected_metric)
            if cohort_df.empty:
                st.info("コホート分析に十分なデータがありません。")
            else:
                fig = px.line(
                    cohort_df,
                    x='days',
                    y='value',
                    color='cohort',
                    markers=True,
                    labels={
                        'days': '公開からの日数',
                        'value': selected_metric_label,
                        'cohort': '公開月'
                    },
                    title="公開月コホート別の平均推移"
                )
                fig.update_layout(height=520)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(cohort_df, use_container_width=True)
        st.markdown('</section>', unsafe_allow_html=True)
    
    with anomaly_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("日次指標の成長率と異常検知")
        st.caption("日次合計指標の変化率を監視し、急激な増減をハイライト")
        
        if history_full_df.empty:
            st.info("統計履歴データが不足しています。")
        else:
            anomaly_df = detect_growth_anomalies(history_full_df, selected_metric)
            if anomaly_df.empty:
                st.info("異常を検出するためのデータが不足しています。")
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=anomaly_df['date'],
                    y=anomaly_df['value'],
                    mode='lines',
                    name=f"日次{selected_metric_label}"
                ))
                anomalies_only = anomaly_df[anomaly_df['is_anomaly']]
                if not anomalies_only.empty:
                    fig.add_trace(go.Scatter(
                        x=anomalies_only['date'],
                        y=anomalies_only['value'],
                        mode='markers',
                        marker=dict(color='#ff006e', size=10),
                        name='異常値'
                    ))
                fig.update_layout(
                    height=520,
                    xaxis_title="日付",
                    yaxis_title=selected_metric_label,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                if anomalies_only.empty:
                    st.info("異常値は検出されませんでした。")
                else:
                    st.subheader("検出された異常値")
                    st.markdown('<div class="glass-table">', unsafe_allow_html=True)
                    st.dataframe(
                        anomalies_only[['date', 'value', 'change_pct', 'z_score']].reset_index(drop=True),
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</section>', unsafe_allow_html=True)
    
    with combo_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("タグの組み合わせ別パフォーマンス")
        st.caption("よく一緒に使われるタグのセットがどの指標を押し上げているかを確認")
        
        combo_df = compute_tag_combinations(videos_df, selected_metric)
        if combo_df.empty:
            st.info("タグの組み合わせを分析できるデータが不足しています。")
        else:
            fig = px.bar(
                combo_df,
                x=selected_metric,
                y='combination',
                orientation='h',
                labels={
                    selected_metric: selected_metric_label,
                    'combination': 'タグの組み合わせ'
                },
                title="上位タグ組み合わせ"
            )
            fig.update_layout(height=520, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(combo_df, use_container_width=True)
        st.markdown('</section>', unsafe_allow_html=True)
    
    with funnel_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("視聴 → いいね → コメントのファネル")
        st.caption("動画視聴からエンゲージメントまでのコンバージョンを俯瞰")
        
        funnel_data = compute_funnel_metrics(videos_df)
        if not funnel_data:
            st.info("ファネルを計算するためのデータが不足しています。")
        else:
            stages = [stage['stage'] for stage in funnel_data]
            values = [stage['value'] for stage in funnel_data]
            conversion_text = [f"{stage['conversion'] * 100:.1f}%" for stage in funnel_data]
            
            fig = go.Figure(go.Funnel(
                y=stages,
                x=values,
                text=conversion_text,
                textposition="inside",
                textinfo="text+value",
                marker=dict(color=['#ef4444', '#fb7185', '#fda4af'])
            ))
            fig.update_layout(height=520)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            for col, stage in zip((col1, col2, col3), funnel_data):
                col.metric(
                    stage['stage'],
                    f"{stage['value']:,}",
                    f"{stage['conversion'] * 100:.1f}%"
                )
        st.markdown('</section>', unsafe_allow_html=True)
    
    with revenue_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("RPMベースの収益シミュレーション")
        st.caption("想定RPMの入力だけで動画ごとの推定収益を試算")
        
        rpm = st.slider("想定RPM（円）", min_value=100, max_value=8000, value=1200, step=50)
        revenue_summary = simulate_revenue(videos_df, rpm)
        
        st.metric("推定総収益", f"¥{revenue_summary['total_estimated']:,.0f}")
        if not revenue_summary['per_video'].empty:
            revenue_df = revenue_summary['per_video'].rename(columns={
                'title': 'タイトル',
                'view_count': '再生数',
                'estimated_revenue': '推定収益（円）'
            })
            st.markdown('<div class="glass-table">', unsafe_allow_html=True)
            st.dataframe(revenue_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("収益を計算できる動画データが不足しています。")
        st.markdown('</section>', unsafe_allow_html=True)
    
    with compare_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("複数チャンネルの比較")
        st.caption("登録者数 / 総再生数 / 動画数を横並びで比較")
        
        comparison_options = {f"{ch['title']} (ID: {ch['id']})": ch['id'] for ch in channels}
        default_selection = [selected_channel['id']] if selected_channel else []
        selected_for_compare = st.multiselect(
            "比較対象チャンネル",
            options=list(comparison_options.keys()),
            default=[key for key, value in comparison_options.items() if value in default_selection]
        )
        selected_ids = [comparison_options[name] for name in selected_for_compare]
        comparison_df = build_channel_comparison(channels, selected_ids)
        
        if comparison_df.empty:
            st.info("比較するチャンネルを2つ以上選択してください。")
        else:
            melted = comparison_df.melt(
                id_vars=['title'],
                value_vars=['subscriber_count', 'view_count', 'video_count'],
                var_name='metric',
                value_name='value'
            )
            metric_labels = {
                'subscriber_count': '登録者数',
                'view_count': '総再生数',
                'video_count': '動画数'
            }
            melted['metric_label'] = melted['metric'].map(metric_labels)
            fig = px.bar(
                melted,
                x='title',
                y='value',
                color='metric_label',
                barmode='group',
                text_auto='.2s',
                labels={'title': 'チャンネル', 'value': '値', 'metric_label': '指標'},
                title="チャンネル指標の比較"
            )
            fig.update_layout(height=520)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(comparison_df, use_container_width=True)
        st.markdown('</section>', unsafe_allow_html=True)
    
    with insight_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("自動インサイト")
        st.caption("動画データをもとに簡易なテキスト洞察を生成")
        
        insights = generate_auto_insights(videos_df, selected_metric, metric_label=selected_metric_label)
        if not insights:
            st.info("インサイト生成に必要なデータが不足しています。")
        else:
            for insight in insights:
                st.markdown(f"<p class='stat-pill'>{insight}</p>", unsafe_allow_html=True)
        st.markdown('</section>', unsafe_allow_html=True)
    
    with schedule_tab:
        st.markdown('<section class="tab-card">', unsafe_allow_html=True)
        st.subheader("おすすめの配信タイミング")
        st.caption("曜日×時間帯ヒートマップから次回の公開候補を提示")
        
        suggestions = suggest_publish_slots(heatmap_df, top_n=5)
        if not suggestions:
            st.info("公開タイミングを提案できるデータが不足しています。")
        else:
            weekday_map = {
                'Monday': '月曜日',
                'Tuesday': '火曜日',
                'Wednesday': '水曜日',
                'Thursday': '木曜日',
                'Friday': '金曜日',
                'Saturday': '土曜日',
                'Sunday': '日曜日',
            }
            suggestion_cols = st.columns(len(suggestions))
            for col, suggestion in zip(suggestion_cols, suggestions):
                weekday_label = weekday_map.get(suggestion['weekday'], suggestion['weekday'])
                col.metric(
                    f"{weekday_label} {suggestion['hour']}時台",
                    f"{suggestion['value']:,.0f}",
                    "推奨"
                )
        st.markdown('</section>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

