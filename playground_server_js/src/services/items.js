const { db } = require("../database");
const { HttpError } = require("../errors");

function getItem(id) {
  const row = db.prepare("SELECT * FROM items WHERE id = ?").get(id);
  if (!row) throw new HttpError(404, "Item não encontrado");
  return row;
}

function listItems(skip, limit) {
  return db.prepare("SELECT * FROM items LIMIT ? OFFSET ?").all(limit, skip);
}

function createItem(data) {
  const info = db
    .prepare("INSERT INTO items (name, description, price, quantity) VALUES (?, ?, ?, ?)")
    .run(data.name, data.description ?? null, data.price, data.quantity ?? 0);
  return getItem(info.lastInsertRowid);
}

function updateItem(id, data) {
  getItem(id);
  db.prepare("UPDATE items SET name=?, description=?, price=?, quantity=? WHERE id=?").run(
    data.name,
    data.description ?? null,
    data.price,
    data.quantity,
    id
  );
  return getItem(id);
}

function patchItem(id, data) {
  getItem(id);
  const fields = [];
  const values = [];
  for (const [k, v] of Object.entries(data)) {
    fields.push(`${k} = ?`);
    values.push(v);
  }
  if (fields.length) {
    values.push(id);
    db.prepare(`UPDATE items SET ${fields.join(", ")} WHERE id = ?`).run(...values);
  }
  return getItem(id);
}

function deleteItem(id) {
  getItem(id);
  db.prepare("DELETE FROM items WHERE id = ?").run(id);
}

module.exports = { listItems, getItem, createItem, updateItem, patchItem, deleteItem };
