const express = require("express");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const { randomUUID } = require("crypto");

const { APP_TITLE, APP_VERSION, ADMIN_EMAIL, ADMIN_NAME, PORT } = require("./src/config");
const { db, initDb } = require("./src/database");
const { logger, maskApiKey } = require("./src/logging");
const { HttpError } = require("./src/errors");

const usersRouter = require("./src/routes/users");
const itemsRouter = require("./src/routes/items");
const salesRouter = require("./src/routes/sales");

function seedAdmin() {
  const existing = db.prepare("SELECT * FROM users WHERE email = ?").get(ADMIN_EMAIL);
  if (existing) {
    logger.info(`Admin already exists | email=${existing.email} | api_key=${maskApiKey(existing.api_key)}`);
    return;
  }
  const apiKey = randomUUID();
  db.prepare(
    "INSERT INTO users (name, email, role, api_key, active) VALUES (?, ?, 'admin', ?, 1)"
  ).run(ADMIN_NAME, ADMIN_EMAIL, apiKey);
  logger.info(`Admin user created | email=${ADMIN_EMAIL} | api_key=${maskApiKey(apiKey)}`);
  const bar = "=".repeat(50);
  process.stdout.write(`\n${bar}\n  Usuário admin criado com sucesso!\n  Email:   ${ADMIN_EMAIL}\n  API Key: ${apiKey}\n  GUARDE ESTA API KEY!\n${bar}\n\n`);
}

initDb();
seedAdmin();

const app = express();
app.use(cors());
app.use(express.json());

// Request logger
app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on("finish", () => {
    const elapsedMs = Number(process.hrtime.bigint() - start) / 1e6;
    const user = req.userEmail || "anonymous";
    const line = `${req.method} ${req.path} -> ${res.statusCode} | user=${user} | elapsed=${elapsedMs.toFixed(1)}ms`;
    if (res.statusCode >= 500) logger.error(line);
    else if (res.statusCode >= 400) logger.warn(line);
    else logger.info(line);
  });
  next();
});

// Rate limit: 60/min, key = api key or IP. Exempt root/health.
const limiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 60,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.header("x-api-key") || req.ip,
  skip: (req) => req.path === "/" || req.path === "/health",
  handler: (req, res) => {
    const key = req.header("x-api-key") || req.ip;
    const user = req.userEmail || "anonymous";
    logger.warn(
      `RateLimit exceeded | ${req.method} ${req.path} | key=${maskApiKey(key)} | user=${user}`
    );
    res
      .status(429)
      .set("Retry-After", "60")
      .json({ detail: "Rate limit exceeded: 60 per 1 minute. Try again in a minute." });
  },
});
app.use(limiter);

app.get("/", (req, res) => {
  res.json({ message: "REST Server ativo. Versão JS/Express." });
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.use("/users", usersRouter);
app.use("/items", itemsRouter);
app.use("/sales", salesRouter);

// 404
app.use((req, res, next) => {
  next(new HttpError(404, "Not Found"));
});

// Global error handler
app.use((err, req, res, _next) => {
  const user = req.userEmail || "anonymous";
  if (err instanceof HttpError) {
    if (err.status >= 500) {
      logger.error(`HTTPException | ${req.method} ${req.path} | status=${err.status} | user=${user} | detail=${JSON.stringify(err.detail)}`);
    } else {
      logger.warn(`HTTPException | ${req.method} ${req.path} | status=${err.status} | user=${user} | detail=${JSON.stringify(err.detail)}`);
    }
    return res.status(err.status).json({ detail: err.detail });
  }
  logger.error(`Unhandled exception | ${req.method} ${req.path} | user=${user}`);
  logger.error(err.stack || String(err));
  res.status(500).json({ detail: "Internal Server Error" });
});

app.listen(PORT, () => {
  logger.info(`Starting app | title=${APP_TITLE} | version=${APP_VERSION} | port=${PORT}`);
});
