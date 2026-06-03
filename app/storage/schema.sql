CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  ended_at TEXT,
  name TEXT NOT NULL,
  mode TEXT NOT NULL,
  notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS shots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  club TEXT NOT NULL,
  source_mode TEXT NOT NULL,
  club_speed_mph REAL,
  face_angle_deg REAL,
  path_deg REAL,
  contact_point REAL,
  carry_yards REAL,
  lateral_yards REAL,
  shot_shape TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
