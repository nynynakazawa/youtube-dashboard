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
);

CREATE TABLE videos (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  channel_id BIGINT NOT NULL,
  youtube_video_id VARCHAR(64) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  published_at TIMESTAMP NOT NULL,
  duration_sec INT,
  tags_json JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
  INDEX idx_channel_id (channel_id),
  INDEX idx_published_at (published_at),
  INDEX idx_channel_published (channel_id, published_at)
);

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
);


