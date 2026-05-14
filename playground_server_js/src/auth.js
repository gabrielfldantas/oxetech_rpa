const { db } = require("./database");
const { logger } = require("./logging");
const { HttpError } = require("./errors");

const ROLE_HIERARCHY = { admin: 4, manager: 3, seller: 2, viewer: 1 };
const VALID_ROLES = new Set(Object.keys(ROLE_HIERARCHY));

function toUser(row) {
  if (!row) return null;
  return { ...row, active: !!row.active };
}

function getUserByApiKey(key) {
  const row = db.prepare("SELECT * FROM users WHERE api_key = ?").get(key);
  return toUser(row);
}

function requireAuth(req, res, next) {
  const key = req.header("x-api-key");
  if (!key) {
    logger.warn(`Auth failed | missing api_key | path=${req.path}`);
    return next(new HttpError(401, "API Key inválida ou usuário inativo"));
  }
  const user = getUserByApiKey(key);
  if (!user || !user.active) {
    logger.warn(`Auth failed | unknown/inactive api_key | path=${req.path}`);
    return next(new HttpError(401, "API Key inválida ou usuário inativo"));
  }
  req.user = user;
  req.userEmail = user.email;
  next();
}

function requireRole(...allowed) {
  return (req, res, next) => {
    if (!req.user) return next(new HttpError(401, "Não autenticado"));
    if (!allowed.includes(req.user.role)) {
      logger.warn(
        `Authz denied | email=${req.user.email} | role=${req.user.role} | required=${allowed.join(",")} | path=${req.path}`
      );
      return next(
        new HttpError(403, `Permissão negada. Roles permitidas: ${allowed.join(", ")}`)
      );
    }
    next();
  };
}

module.exports = { requireAuth, requireRole, VALID_ROLES, ROLE_HIERARCHY };
