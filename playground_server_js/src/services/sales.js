const { db, transaction } = require("../database");
const { HttpError } = require("../errors");

function getSale(id) {
  const row = db.prepare("SELECT * FROM sales WHERE id = ?").get(id);
  if (!row) throw new HttpError(404, "Venda não encontrada");
  return row;
}

function listSales(skip, limit) {
  return db.prepare("SELECT * FROM sales LIMIT ? OFFSET ?").all(limit, skip);
}

function _getItem(id) {
  const row = db.prepare("SELECT * FROM items WHERE id = ?").get(id);
  if (!row) throw new HttpError(404, "Item não encontrado");
  return row;
}

function createSale(data, currentUser) {
  const tx = transaction(() => {
    const item = _getItem(data.item_id);
    if (item.quantity < data.quantity) {
      throw new HttpError(400, `Estoque insuficiente. Disponível: ${item.quantity}`);
    }
    const total = Math.round(item.price * data.quantity * 100) / 100;
    const info = db
      .prepare(
        "INSERT INTO sales (user_id, item_id, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?)"
      )
      .run(currentUser.id, data.item_id, data.quantity, item.price, total);
    db.prepare("UPDATE items SET quantity = quantity - ? WHERE id = ?").run(
      data.quantity,
      data.item_id
    );
    return getSale(info.lastInsertRowid);
  });
  return tx();
}

function updateSale(id, data) {
  const tx = transaction(() => {
    const sale = getSale(id);
    const item = _getItem(data.item_id);
    // restore old stock
    db.prepare("UPDATE items SET quantity = quantity + ? WHERE id = ?").run(
      sale.quantity,
      sale.item_id
    );
    const fresh = _getItem(data.item_id);
    if (fresh.quantity < data.quantity) {
      throw new HttpError(400, `Estoque insuficiente. Disponível: ${fresh.quantity}`);
    }
    const total = Math.round(item.price * data.quantity * 100) / 100;
    db.prepare(
      "UPDATE sales SET item_id=?, quantity=?, unit_price=?, total=? WHERE id=?"
    ).run(data.item_id, data.quantity, item.price, total, id);
    db.prepare("UPDATE items SET quantity = quantity - ? WHERE id = ?").run(
      data.quantity,
      data.item_id
    );
    return getSale(id);
  });
  return tx();
}

function patchSale(id, data) {
  const tx = transaction(() => {
    const sale = getSale(id);
    const item_id = data.item_id ?? sale.item_id;
    const quantity = data.quantity ?? sale.quantity;
    const item = _getItem(item_id);
    // restore old stock
    db.prepare("UPDATE items SET quantity = quantity + ? WHERE id = ?").run(
      sale.quantity,
      sale.item_id
    );
    const fresh = _getItem(item_id);
    if (fresh.quantity < quantity) {
      throw new HttpError(400, `Estoque insuficiente. Disponível: ${fresh.quantity}`);
    }
    const total = Math.round(item.price * quantity * 100) / 100;
    db.prepare(
      "UPDATE sales SET item_id=?, quantity=?, unit_price=?, total=? WHERE id=?"
    ).run(item_id, quantity, item.price, total, id);
    db.prepare("UPDATE items SET quantity = quantity - ? WHERE id = ?").run(quantity, item_id);
    return getSale(id);
  });
  return tx();
}

function deleteSale(id) {
  const tx = transaction(() => {
    const sale = getSale(id);
    db.prepare("UPDATE items SET quantity = quantity + ? WHERE id = ?").run(
      sale.quantity,
      sale.item_id
    );
    db.prepare("DELETE FROM sales WHERE id = ?").run(id);
  });
  tx();
}

module.exports = { listSales, getSale, createSale, updateSale, patchSale, deleteSale };
