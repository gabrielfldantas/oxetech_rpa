const { Router } = require("express");
const svc = require("../services/items");
const { requireAuth, requireRole } = require("../auth");
const { validate } = require("../validate");
const { ItemCreate, ItemUpdate, ItemPatch, Pagination, IdParam } = require("../schemas");

const router = Router();
const readAccess = [requireAuth, requireRole("admin", "manager", "seller", "viewer")];
const writeAccess = [requireAuth, requireRole("admin", "manager")];

router.get("/", readAccess, validate(Pagination, "query"), (req, res) => {
  res.json(svc.listItems(req.query.skip, req.query.limit));
});

router.get("/:id", readAccess, validate(IdParam, "params"), (req, res) => {
  res.json(svc.getItem(req.params.id));
});

router.post("/", writeAccess, validate(ItemCreate, "body"), (req, res) => {
  res.status(201).json(svc.createItem(req.body));
});

router.put("/:id", writeAccess, validate(IdParam, "params"), validate(ItemUpdate, "body"), (req, res) => {
  res.json(svc.updateItem(req.params.id, req.body));
});

router.patch("/:id", writeAccess, validate(IdParam, "params"), validate(ItemPatch, "body"), (req, res) => {
  res.json(svc.patchItem(req.params.id, req.body));
});

router.delete("/:id", writeAccess, validate(IdParam, "params"), (req, res) => {
  svc.deleteItem(req.params.id);
  res.status(204).end();
});

module.exports = router;
