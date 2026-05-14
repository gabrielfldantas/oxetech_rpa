const { DatabaseSync } = require("node:sqlite");
const { DATABASE_PATH } = require("./config");

const db = new DatabaseSync(DATABASE_PATH);
db.exec("PRAGMA journal_mode = WAL");
db.exec("PRAGMA foreign_keys = ON");

function transaction(fn) {
  return (...args) => {
    db.exec("BEGIN");
    try {
      const result = fn(...args);
      db.exec("COMMIT");
      return result;
    } catch (err) {
      db.exec("ROLLBACK");
      throw err;
    }
  };
}

function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id      INTEGER PRIMARY KEY AUTOINCREMENT,
      name    TEXT    NOT NULL,
      email   TEXT    NOT NULL UNIQUE,
      role    TEXT    NOT NULL DEFAULT 'viewer',
      api_key TEXT    NOT NULL UNIQUE,
      active  INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS items (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      name        TEXT    NOT NULL,
      description TEXT,
      price       REAL    NOT NULL,
      quantity    INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS sales (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id    INTEGER NOT NULL REFERENCES users(id),
      item_id    INTEGER NOT NULL REFERENCES items(id),
      quantity   INTEGER NOT NULL,
      unit_price REAL    NOT NULL,
      total      REAL    NOT NULL,
      created_at TEXT    NOT NULL DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS ix_sales_user_id    ON sales(user_id);
    CREATE INDEX IF NOT EXISTS ix_sales_item_id    ON sales(item_id);
    CREATE INDEX IF NOT EXISTS ix_sales_created_at ON sales(created_at);
  `);
}

module.exports = { db, initDb, transaction };
