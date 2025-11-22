"""
データ処理用のユーティリティ関数
"""
import sys
import os
import json
import itertools
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Sequence

import numpy as np
import pandas as pd

# 親ディレクトリをパスに追加（backend/db/rds.pyをインポートするため）
# streamlit/utils/data_processor.py から backend/ へのパス
backend_path = os.path.join(os.path.dirname(__file__), '../../')
sys.path.insert(0, os.path.abspath(backend_path))

from db.rds import get_db_connection


def get_channels() -> List[Dict[str, Any]]:
    """チャンネル一覧を取得"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, youtube_channel_id, title, subscriber_count, view_count, video_count
                FROM channels
                ORDER BY title
            """)
            return cursor.fetchall()


def get_channel_by_id(channel_id: int) -> Optional[Dict[str, Any]]:
    """チャンネルIDからチャンネル情報を取得"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, youtube_channel_id, title, subscriber_count, view_count, video_count
                FROM channels
                WHERE id = %s
            """, (channel_id,))
            return cursor.fetchone()


def get_channel_by_youtube_id(youtube_channel_id: str) -> Optional[Dict[str, Any]]:
    """YouTubeチャンネルIDからチャンネル情報を取得"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, youtube_channel_id, title, subscriber_count, view_count, video_count
                FROM channels
                WHERE youtube_channel_id = %s
            """, (youtube_channel_id,))
            return cursor.fetchone()


def get_videos_with_stats(channel_id: int) -> pd.DataFrame:
    """チャンネルの動画一覧と最新の統計情報を取得"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    v.id,
                    v.youtube_video_id,
                    v.title,
                    v.published_at,
                    v.duration_sec,
                    v.tags_json,
                    COALESCE(latest_stats.view_count, 0) as view_count,
                    COALESCE(latest_stats.like_count, 0) as like_count,
                    COALESCE(latest_stats.comment_count, 0) as comment_count
                FROM videos v
                LEFT JOIN (
                    SELECT 
                        video_id,
                        view_count,
                        like_count,
                        comment_count,
                        ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY snapshot_at DESC) as rn
                    FROM video_stats_history
                ) latest_stats ON v.id = latest_stats.video_id AND latest_stats.rn = 1
                WHERE v.channel_id = %s
                ORDER BY v.published_at DESC
            """, (channel_id,))
            rows = cursor.fetchall()
            
            if not rows:
                return pd.DataFrame()
            
            df = pd.DataFrame(rows)
            df['published_at'] = pd.to_datetime(df['published_at'])
            return df


def get_video_stats_history(video_ids: List[int], days: int = 30) -> pd.DataFrame:
    """複数動画の統計履歴を取得（公開から指定日数分）"""
    if not video_ids:
        return pd.DataFrame()
    
    placeholders = ','.join(['%s'] * len(video_ids))
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    vsh.video_id,
                    v.youtube_video_id,
                    v.title,
                    v.published_at,
                    vsh.snapshot_at,
                    vsh.view_count,
                    vsh.like_count,
                    vsh.comment_count,
                    DATEDIFF(vsh.snapshot_at, v.published_at) as days_since_publish
                FROM video_stats_history vsh
                JOIN videos v ON vsh.video_id = v.id
                WHERE vsh.video_id IN ({placeholders})
                  AND vsh.snapshot_at >= %s
                ORDER BY vsh.video_id, vsh.snapshot_at
            """, tuple(video_ids) + (cutoff_date,))
            rows = cursor.fetchall()
            
            if not rows:
                return pd.DataFrame()
            
            df = pd.DataFrame(rows)
            df['published_at'] = pd.to_datetime(df['published_at'])
            df['snapshot_at'] = pd.to_datetime(df['snapshot_at'])
            return df


def process_heatmap_data(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """曜日 × 時間帯ヒートマップ用のデータを処理"""
    if df.empty:
        return pd.DataFrame()
    
    df = df.copy()
    df['weekday'] = df['published_at'].dt.day_name()
    df['hour'] = df['published_at'].dt.hour
    
    # 曜日の順序を定義
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)
    
    # 指標の平均値を計算
    heatmap_data = df.groupby(['weekday', 'hour'])[metric].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values=metric)
    
    return heatmap_pivot


def process_tag_performance(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """タグ別の平均パフォーマンスを計算"""
    if df.empty:
        return pd.DataFrame()
    
    tag_metrics = []
    
    for _, row in df.iterrows():
        tags = _extract_tags(row.get('tags_json'))
        if not tags:
            continue
        
        metric_value = row.get(metric, 0)
        for tag in tags:
            tag_metrics.append({
                'tag': tag,
                metric: metric_value
            })
    
    if not tag_metrics:
        return pd.DataFrame()
    
    tag_df = pd.DataFrame(tag_metrics)
    tag_performance = tag_df.groupby('tag')[metric].mean().sort_values(ascending=False).reset_index()
    
    return tag_performance


def _extract_tags(tags_json_field: Any) -> List[str]:
    if not tags_json_field:
        return []
    
    try:
        tags = json.loads(tags_json_field) if isinstance(tags_json_field, str) else tags_json_field
    except (json.JSONDecodeError, TypeError):
        return []
    
    if not isinstance(tags, list):
        return []
    
    return [tag for tag in tags if isinstance(tag, str) and tag.strip()]


def compute_cohort_performance(history_df: pd.DataFrame, metric: str, checkpoints: Sequence[int] = (30, 90)) -> pd.DataFrame:
    """公開月ごとのコホート平均を算出"""
    if history_df.empty:
        return pd.DataFrame()
    
    df = history_df.copy()
    df['cohort'] = df['published_at'].dt.to_period('M').astype(str)
    df = df.sort_values(['video_id', 'snapshot_at'])
    
    records: List[Dict[str, Any]] = []
    
    for (video_id, cohort), group in df.groupby(['video_id', 'cohort']):
        for checkpoint in checkpoints:
            eligible = group[group['days_since_publish'] <= checkpoint]
            if eligible.empty:
                continue
            value = eligible.iloc[-1][metric]
            records.append({
                'cohort': cohort,
                'days': checkpoint,
                'value': value
            })
    
    if not records:
        return pd.DataFrame()
    
    cohort_df = pd.DataFrame(records)
    return (
        cohort_df.groupby(['cohort', 'days'])['value']
        .mean()
        .reset_index()
        .sort_values(['cohort', 'days'])
    )


def detect_growth_anomalies(history_df: pd.DataFrame, metric: str, window: int = 7, z_threshold: float = 2.0) -> pd.DataFrame:
    """指標の急激な変化を検出"""
    if history_df.empty:
        return pd.DataFrame()
    
    timeline = (
        history_df.groupby('snapshot_at')[metric]
        .sum()
        .sort_index()
    )
    
    df = timeline.to_frame(name='value').reset_index()
    df.rename(columns={'snapshot_at': 'date'}, inplace=True)
    df['change_pct'] = df['value'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
    rolling_mean = df['change_pct'].rolling(window).mean()
    rolling_std = df['change_pct'].rolling(window).std().replace(0, np.nan)
    
    df['z_score'] = ((df['change_pct'] - rolling_mean) / rolling_std).replace([np.inf, -np.inf], np.nan).fillna(0)
    df['is_anomaly'] = df['z_score'].abs() >= z_threshold
    
    return df


def compute_tag_combinations(df: pd.DataFrame, metric: str, top_n: int = 20) -> pd.DataFrame:
    """タグの組み合わせごとの平均パフォーマンス"""
    if df.empty:
        return pd.DataFrame()
    
    combo_metrics: Dict[str, List[float]] = {}
    
    for _, row in df.iterrows():
        tags = sorted(set(_extract_tags(row.get('tags_json'))))
        if len(tags) < 2:
            continue
        metric_value = row.get(metric, 0)
        for combo in itertools.combinations(tags, 2):
            key = ' + '.join(combo)
            combo_metrics.setdefault(key, []).append(metric_value)
    
    if not combo_metrics:
        return pd.DataFrame()
    
    data = [
        {'combination': combo, metric: float(np.mean(values))}
        for combo, values in combo_metrics.items()
    ]
    combo_df = pd.DataFrame(data).sort_values(metric, ascending=False)
    return combo_df.head(top_n)


def compute_funnel_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """視聴→いいね→コメントのコンバージョンを算出"""
    if df.empty:
        return []
    
    total_views = df['view_count'].sum()
    total_likes = df['like_count'].sum()
    total_comments = df['comment_count'].sum()
    
    def safe_ratio(numerator: float, denominator: float) -> float:
        return float(numerator / denominator) if denominator else 0.0
    
    return [
        {'stage': '視聴', 'value': int(total_views), 'conversion': 1.0},
        {'stage': 'いいね', 'value': int(total_likes), 'conversion': safe_ratio(total_likes, total_views)},
        {'stage': 'コメント', 'value': int(total_comments), 'conversion': safe_ratio(total_comments, total_likes)},
    ]


def simulate_revenue(df: pd.DataFrame, rpm: float) -> Dict[str, Any]:
    """RPMベースの収益試算"""
    if df.empty:
        return {'total_estimated': 0.0, 'per_video': pd.DataFrame(), 'rpm': rpm}
    
    total_views = df['view_count'].sum()
    total_estimated = (total_views / 1000) * rpm
    
    top_videos = df[['title', 'view_count']].copy()
    top_videos['estimated_revenue'] = (top_videos['view_count'] / 1000) * rpm
    top_videos = top_videos.sort_values('view_count', ascending=False).head(10)
    
    return {
        'total_estimated': total_estimated,
        'per_video': top_videos,
        'rpm': rpm
    }


def build_channel_comparison(channels: List[Dict[str, Any]], selected_ids: Sequence[int]) -> pd.DataFrame:
    """複数チャンネルの比較用データ"""
    if not selected_ids:
        return pd.DataFrame()
    
    selected = [channel for channel in channels if channel['id'] in selected_ids]
    if not selected:
        return pd.DataFrame()
    
    df = pd.DataFrame(selected)
    return df[['id', 'title', 'subscriber_count', 'view_count', 'video_count']].sort_values('subscriber_count', ascending=False)


def generate_auto_insights(df: pd.DataFrame, metric: str, metric_label: Optional[str] = None, top_n: int = 3) -> List[str]:
    """動画データから定性的なインサイトを生成"""
    if df.empty:
        return []
    
    insights: List[str] = []
    label = metric_label or metric
    
    # トップパフォーマンス
    top_video = df.sort_values(metric, ascending=False).iloc[0]
    insights.append(
        f"直近で最も{label}が高い動画は「{top_video['title']}」で、{int(top_video[metric]):,}を記録しています。"
    )
    
    # 公開後30日以内の好調動画
    tzinfo = df['published_at'].dt.tz
    recent_threshold = (pd.Timestamp.now(tz=tzinfo) - pd.Timedelta(days=30)) if tzinfo is not None else (pd.Timestamp.now() - pd.Timedelta(days=30))
    recent_videos = df[df['published_at'] >= recent_threshold]
    if not recent_videos.empty:
        recent_top = recent_videos.sort_values(metric, ascending=False).iloc[0]
        insights.append(
            f"直近30日で最も{label}を伸ばしたのは「{recent_top['title']}」で、{int(recent_top[metric]):,}を達成しました。"
        )
    
    # 長尺 vs 短尺の傾向
    df = df.copy()
    df['duration_min'] = df['duration_sec'] / 60
    shorter = df[df['duration_min'] < df['duration_min'].median()]
    longer = df[df['duration_min'] >= df['duration_min'].median()]
    if not shorter.empty and not longer.empty:
        short_avg = shorter[metric].mean()
        long_avg = longer[metric].mean()
        dominant = "短尺" if short_avg > long_avg else "長尺"
        insights.append(
            f"{dominant}動画の平均{label}が高く、短尺: {short_avg:,.0f} / 長尺: {long_avg:,.0f} です。"
        )
    
    return insights[:top_n]


def suggest_publish_slots(heatmap_df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """ヒートマップからおすすめの公開時間帯を抽出"""
    if heatmap_df is None or heatmap_df.empty:
        return []
    
    stacked = (
        heatmap_df.stack()
        .reset_index()
        .rename(columns={'weekday': 'weekday', 'hour': 'hour', 0: 'value'})
    )
    stacked = stacked.sort_values('value', ascending=False).head(top_n)
    
    return [
        {'weekday': row['weekday'], 'hour': int(row['hour']), 'value': row['value']}
        for _, row in stacked.iterrows()
    ]

