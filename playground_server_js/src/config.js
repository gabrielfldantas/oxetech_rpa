const path = require("path");

module.exports = {
  DATABASE_PATH: process.env.DATABASE_PATH || path.join(process.cwd(), "database.db"),
  APP_TITLE: "REST Server — Curso de Integrações (JS)",
  APP_DESCRIPTION:
    "Servidor REST modular para prática de integrações de sistemas. " +
    "Autenticação via API Key (header X-API-Key) com controle de acesso por roles.",
  APP_VERSION: "0.1.0",
  ADMIN_NAME: "Admin",
  ADMIN_EMAIL: "admin@local.com",
  PORT: parseInt(process.env.PORT || "8000", 10),
};
