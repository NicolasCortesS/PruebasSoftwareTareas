CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','viewer')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  name VARCHAR(140) NOT NULL,
  description TEXT,
  starts_at TIMESTAMPTZ NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('Charla','Taller','Show','Otro')),
  price INTEGER NOT NULL CHECK (price >= 0),
  seats_total INTEGER NOT NULL CHECK (seats_total >= 0),
  seats_sold INTEGER NOT NULL DEFAULT 0 CHECK (seats_sold >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS movements (
  id SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('SALE','REFUND')),
  qty INTEGER NOT NULL CHECK (qty > 0),
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
