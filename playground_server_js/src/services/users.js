const { randomUUID } = require("crypto");
const { db } = require("../database");
const { HttpError } = require("../errors");
const { VALID_ROLES } = require("../auth");

function rowToUser(row) {
  if (!row) return null;
  return { ...row, active: !!row.active };
}

function publicUser(u) {
  const { api_key, ...rest } = u;
  return rest;
}

function listUsers(skip, limit) {
  const rows = db.prepare("SELECT * FROM users LIMIT ? OFFSET ?").all(limit, skip);
  return rows.map(rowToUser).map(publicUser);
}

function getUser(id) {
  const row = db.prepare("SELECT * FROM users WHERE id = ?").get(id);
  if (!row) throw new HttpError(404, "Usuário não encontrado");
  return publicUser(rowToUser(row));
}

function _getRawUser(id) {
  const row = db.prepare("SELECT * FROM users WHERE id = ?").get(id);
  if (!row) throw new HttpError(404, "Usuário não encontrado");
  return rowToUser(row);
}

function createUser(data) {
  if (!VALID_ROLES.has(data.role)) {
    throw new HttpError(400, `Role inválida. Opções: ${[...VALID_ROLES].sort().join(", ")}`);
  }
  const existing = db.prepare("SELECT id FROM users WHERE email = ?").get(data.email);
  if (existing) throw new HttpError(409, "Email já cadastrado");
  const apiKey = randomUUID();
  const info = db
    .prepare("INSERT INTO users (name, email, role, api_key, active) VALUES (?, ?, ?, ?, 1)")
    .run(data.name, data.email, data.role, apiKey);
  return rowToUser(db.prepare("SELECT * FROM users WHERE id = ?").get(info.lastInsertRowid));
}

function updateUser(id, data) {
  _getRawUser(id);
  if (!VALID_ROLES.has(data.role)) {
    throw new HttpError(400, `Role inválida. Opções: ${[...VALID_ROLES].sort().join(", ")}`);
  }
  const dup = db.prepare("SELECT id FROM users WHERE email = ? AND id != ?").get(data.email, id);
  if (dup) throw new HttpError(409, "Email já cadastrado");
  db.prepare("UPDATE users SET name=?, email=?, role=?, active=? WHERE id=?").run(
    data.name,
    data.email,
    data.role,
    data.active ? 1 : 0,
    id
  );
  return getUser(id);
}

function patchUser(id, data) {
  _getRawUser(id);
  if (data.role && !VALID_ROLES.has(data.role)) {
    throw new HttpError(400, `Role inválida. Opções: ${[...VALID_ROLES].sort().join(", ")}`);
  }
  if (data.email) {
    const dup = db.prepare("SELECT id FROM users WHERE email = ? AND id != ?").get(data.email, id);
    if (dup) throw new HttpError(409, "Email já cadastrado");
  }
  const fields = [];
  const values = [];
  for (const [k, v] of Object.entries(data)) {
    fields.push(`${k} = ?`);
    values.push(k === "active" ? (v ? 1 : 0) : v);
  }
  if (fields.length) {
    values.push(id);
    db.prepare(`UPDATE users SET ${fields.join(", ")} WHERE id = ?`).run(...values);
  }
  return getUser(id);
}

function deleteUser(id) {
  _getRawUser(id);
  db.prepare("DELETE FROM users WHERE id = ?").run(id);
}

module.exports = { listUsers, getUser, createUser, updateUser, patchUser, deleteUser };
