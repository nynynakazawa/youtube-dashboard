"""
一時的なスクリプト: RDSにデータベースとテーブルを作成する
このスクリプトはLambda関数として実行し、データベースとテーブルを作成します
"""
import pymysql
from typing import Dict, Any

from constants.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda関数ハンドラー: データベースとテーブルを作成
    """
    try:
        # まず、データベース名を指定せずに接続（MySQLサーバーに接続）
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor,
        )
        
        try:
            with connection.cursor() as cursor:
                # データベースが存在するか確認
                cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
                db_exists = cursor.fetchone()
                
                if not db_exists:
                    # データベースを作成
                    cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"データベース '{DB_NAME}' を作成しました")
                else:
                    print(f"データベース '{DB_NAME}' は既に存在します")
                
                # 作成したデータベースを選択
                cursor.execute(f"USE {DB_NAME}")
                
                # テーブルが存在するか確認
                cursor.execute("SHOW TABLES LIKE 'channels'")
                table_exists = cursor.fetchone()
                
                if not table_exists:
                    # channelsテーブルを作成
                    cursor.execute("""
                        CREATE TABLE channels (
                          id BIGINT PRIMARY KEY AUTO_INCREMENT,
                          youtube_channel_id VARCHAR(64) UNIQUE NOT NULL,
                          title VARCHAR(255) NOT NULL,
                          description TEXT,
                          published_at TIMESTAMP,
                          subscriber_count BIGINT,
                          video_count INT,
                          view_count BIGINT,
                          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          INDEX idx_youtube_channel_id (youtube_channel_id)
                        )
                    """)
                    print("テーブル 'channels' を作成しました")
                
                # videosテーブルを作成
                cursor.execute("SHOW TABLES LIKE 'videos'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE videos (
                          id BIGINT PRIMARY KEY AUTO_INCREMENT,
                          channel_id BIGINT NOT NULL,
                          youtube_video_id VARCHAR(64) UNIQUE NOT NULL,
                          title VARCHAR(255) NOT NULL,
                          description TEXT,
                          published_at TIMESTAMP NOT NULL,
                          duration_sec INT,
                          tags_json JSON,
                          view_count BIGINT,
                          like_count BIGINT,
                          comment_count BIGINT,
                          thumbnail_url VARCHAR(512),
                          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
                          INDEX idx_channel_id (channel_id),
                          INDEX idx_published_at (published_at),
                          INDEX idx_channel_published (channel_id, published_at)
                        )
                    """)
                    print("テーブル 'videos' を作成しました")
                
                # video_stats_historyテーブルを作成
                cursor.execute("SHOW TABLES LIKE 'video_stats_history'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE video_stats_history (
                          id BIGINT PRIMARY KEY AUTO_INCREMENT,
                          video_id BIGINT NOT NULL,
                          snapshot_at TIMESTAMP NOT NULL,
                          view_count BIGINT NOT NULL,
                          like_count BIGINT,
                          comment_count BIGINT,
                          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
                          INDEX idx_video_snapshot (video_id, snapshot_at)
                        )
                    """)
                    print("テーブル 'video_stats_history' を作成しました")
                
                connection.commit()
                print("すべてのテーブルが正常に作成されました")
                
                return {
                    "statusCode": 200,
                    "body": {
                        "message": "データベースとテーブルの作成が完了しました",
                        "database": DB_NAME,
                        "tables": ["channels", "videos", "video_stats_history"]
                    }
                }
        finally:
            connection.close()
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "message": "データベースの作成に失敗しました"
            }
        }

