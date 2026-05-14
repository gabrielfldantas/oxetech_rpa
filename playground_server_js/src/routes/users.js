const { Router } = require("express");
const svc = require("../services/users");
const { requireAuth, requireRole } = require("../auth");
const { validate } = require("../validate");
const { UserCreate, UserUpdate, UserPatch, Pagination, IdParam } = require("../schemas");

const router = Router();
const adminOnly = [requireAuth, requireRole("admin")];

router.get("/", adminOnly, validate(Pagination, "query"), (req, res) => {
  res.json(svc.listUsers(req.query.skip, req.query.limit));
});

router.get("/:id", adminOnly, validate(IdParam, "params"), (req, res) => {
  res.json(svc.getUser(req.params.id));
});

router.post("/", adminOnly, validate(UserCreate, "body"), (req, res) => {
  res.status(201).json(svc.createUser(req.body));
});

router.put("/:id", adminOnly, validate(IdParam, "params"), validate(UserUpdate, "body"), (req, res) => {
  res.json(svc.updateUser(req.params.id, req.body));
});

router.patch("/:id", adminOnly, validate(IdParam, "params"), validate(UserPatch, "body"), (req, res) => {
  res.json(svc.patchUser(req.params.id, req.body));
});

router.delete("/:id", adminOnly, validate(IdParam, "params"), (req, res) => {
  svc.deleteUser(req.params.id);
  res.status(204).end();
});

module.exports = router;
