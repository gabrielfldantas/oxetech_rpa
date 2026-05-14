const { Router } = require("express");
const svc = require("../services/sales");
const { requireAuth, requireRole } = require("../auth");
const { validate } = require("../validate");
const { SaleCreate, SaleUpdate, SalePatch, Pagination, IdParam } = require("../schemas");

const router = Router();
const readAccess = [requireAuth, requireRole("admin", "manager", "seller", "viewer")];
const createAccess = [requireAuth, requireRole("admin", "manager", "seller")];
const writeAccess = [requireAuth, requireRole("admin", "manager")];

router.get("/", readAccess, validate(Pagination, "query"), (req, res) => {
  res.json(svc.listSales(req.query.skip, req.query.limit));
});

router.get("/:id", readAccess, validate(IdParam, "params"), (req, res) => {
  res.json(svc.getSale(req.params.id));
});

router.post("/", createAccess, validate(SaleCreate, "body"), (req, res) => {
  res.status(201).json(svc.createSale(req.body, req.user));
});

router.put("/:id", writeAccess, validate(IdParam, "params"), validate(SaleUpdate, "body"), (req, res) => {
  res.json(svc.updateSale(req.params.id, req.body));
});

router.patch("/:id", writeAccess, validate(IdParam, "params"), validate(SalePatch, "body"), (req, res) => {
  res.json(svc.patchSale(req.params.id, req.body));
});

router.delete("/:id", writeAccess, validate(IdParam, "params"), (req, res) => {
  svc.deleteSale(req.params.id);
  res.status(204).end();
});

module.exports = router;
