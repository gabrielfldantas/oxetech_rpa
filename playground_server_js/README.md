# Playground Server JS — OxeTech RPA

Servidor REST modular construído com **Express** + **SQLite** (via `node:sqlite`, built-in do Node 22+) para prática de integrações de sistemas. Porta JS do `playground_server_py`.

## 🚀 Quick Start

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd oxetech_rpa/playground_server_js

# 2. Instalar dependências (requer Node.js 18+)
npm install

# 3. Rodar o servidor
npm start
# ou em modo dev (reload automático):
npm run dev
```

Na primeira execução o servidor cria automaticamente:
- O banco de dados SQLite (`database.db`)
- O diretório `logs/` com os arquivos `app-YYYY-MM-DD.log` e `error-YYYY-MM-DD.log` (rotacionados diariamente)
- Um usuário **admin** com uma **API Key** exibida no console **apenas uma vez** (na criação)

> ⚠️ **Guarde a API Key do admin!** Em execuções subsequentes apenas a forma mascarada (`****last4`) aparece nos logs. A chave completa **nunca** é gravada em arquivo.

Servidor sobe em `http://localhost:8000` por padrão. Override com a env `PORT`:

```bash
PORT=3000 npm start
```

## 📖 Endpoints públicos

Com o servidor rodando:
- **Root**: [http://localhost:8000/](http://localhost:8000/) — info do servidor
- **Health check**: [http://localhost:8000/health](http://localhost:8000/health) — sem autenticação

> Esta versão JS não inclui Swagger/ReDoc gerado automaticamente como a versão py. Use os exemplos `curl` deste README como referência.

## 🔑 Autenticação

Toda requisição (exceto `/` e `/health`) exige o header `X-API-Key`:

```bash
curl -H "X-API-Key: SUA_API_KEY" http://localhost:8000/users
```

| Código | Significado |
|--------|-------------|
| 401    | API Key inválida ou usuário inativo |
| 403    | Usuário não tem permissão para esta ação |
| 422    | Falha de validação do schema (campo obrigatório faltando, valor fora do intervalo, email mal formatado, role inválida) |
| 429    | Rate limit excedido — máximo 60 req/min por API key |

> A API Key só aparece no corpo da resposta em `POST /users` (criação). Nos demais endpoints de usuário a chave é omitida — use o endpoint de criação para entregar a chave ao novo usuário.

## 👥 Roles e Permissões

| Ação                       | admin | manager | seller | viewer |
|----------------------------|:-----:|:-------:|:------:|:------:|
| `GET /users`               | ✅    | ❌      | ❌     | ❌     |
| `POST /users`              | ✅    | ❌      | ❌     | ❌     |
| `PUT/PATCH/DELETE /users`  | ✅    | ❌      | ❌     | ❌     |
| `GET /items`               | ✅    | ✅      | ✅     | ✅     |
| `POST /items`              | ✅    | ✅      | ❌     | ❌     |
| `PUT/PATCH/DELETE /items`  | ✅    | ✅      | ❌     | ❌     |
| `GET /sales`               | ✅    | ✅      | ✅     | ✅     |
| `POST /sales`              | ✅    | ✅      | ✅     | ❌     |
| `PUT/PATCH/DELETE /sales`  | ✅    | ✅      | ❌     | ❌     |

## 📋 Endpoints

### Users (`/users`)

| Método   | Endpoint          | Descrição            | Role    |
|----------|-------------------|----------------------|---------|
| `GET`    | `/users`          | Listar usuários      | admin   |
| `GET`    | `/users/:id`      | Buscar por ID        | admin   |
| `POST`   | `/users`          | Criar usuário        | admin   |
| `PUT`    | `/users/:id`      | Atualizar completo   | admin   |
| `PATCH`  | `/users/:id`      | Atualizar parcial    | admin   |
| `DELETE` | `/users/:id`      | Remover              | admin   |

### Items (`/items`)

| Método   | Endpoint          | Descrição            | Role            |
|----------|-------------------|----------------------|-----------------|
| `GET`    | `/items`          | Listar itens         | todos           |
| `GET`    | `/items/:id`      | Buscar por ID        | todos           |
| `POST`   | `/items`          | Criar item           | admin, manager  |
| `PUT`    | `/items/:id`      | Atualizar completo   | admin, manager  |
| `PATCH`  | `/items/:id`      | Atualizar parcial    | admin, manager  |
| `DELETE` | `/items/:id`      | Remover              | admin, manager  |

### Sales (`/sales`)

| Método   | Endpoint          | Descrição            | Role                    |
|----------|-------------------|----------------------|-------------------------|
| `GET`    | `/sales`          | Listar vendas        | todos                   |
| `GET`    | `/sales/:id`      | Buscar por ID        | todos                   |
| `POST`   | `/sales`          | Criar venda          | admin, manager, seller  |
| `PUT`    | `/sales/:id`      | Atualizar completo   | admin, manager          |
| `PATCH`  | `/sales/:id`      | Atualizar parcial    | admin, manager          |
| `DELETE` | `/sales/:id`      | Remover              | admin, manager          |

> **Nota:** Ao criar uma venda, o estoque do item é decrementado automaticamente. Ao deletar, o estoque é restaurado. `PUT`/`PATCH` recalculam a diferença (estoque antigo restaurado, novo decrementado) dentro de uma transação SQLite.

### Paginação

`GET /users`, `GET /items` e `GET /sales` aceitam query params:

| Param  | Default | Validação        |
|--------|---------|------------------|
| `skip` | 0       | inteiro ≥ 0      |
| `limit`| 100     | inteiro 1..100   |

```bash
curl -H "X-API-Key: KEY" "http://localhost:8000/items?skip=20&limit=10"
```

## ✅ Validações de Schema

Entradas são validadas no schema **zod** antes de chegar no service. Exemplos que retornam **422**:

- `price <= 0` ou `quantity < 0` em `Item`
- `quantity <= 0`, `quantity > 1_000_000` ou `item_id <= 0` em `Sale` (bloqueia venda negativa que aumentaria estoque)
- `email` mal formatado
- `role` fora de `{admin, manager, seller, viewer}`
- `name` vazio
- Campos extras em `PATCH` (schemas `.strict()`)

Resposta 422 inclui `detail` com a lista de issues do zod (caminho + mensagem).

## 🧪 Exemplos com curl

### 1. Criar um usuário (seller)

```bash
curl -X POST http://localhost:8000/users \
  -H "X-API-Key: SUA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "João", "email": "joao@email.com", "role": "seller"}'
```

Resposta inclui `api_key` — entregue ao novo usuário.

### 2. Criar um item

```bash
curl -X POST http://localhost:8000/items \
  -H "X-API-Key: SUA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Notebook", "description": "Notebook 16GB RAM", "price": 3500.00, "quantity": 10}'
```

### 3. Efetuar uma venda

```bash
curl -X POST http://localhost:8000/sales \
  -H "X-API-Key: API_KEY_DO_SELLER" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 2}'
```

### 4. Listar itens (qualquer role)

```bash
curl -H "X-API-Key: QUALQUER_API_KEY" http://localhost:8000/items
```

### 5. Atualizar parcialmente um item (PATCH)

```bash
curl -X PATCH http://localhost:8000/items/1 \
  -H "X-API-Key: SUA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"price": 3200.00}'
```

### 6. Deletar uma venda

```bash
curl -X DELETE http://localhost:8000/sales/1 \
  -H "X-API-Key: SUA_ADMIN_KEY"
```

## 📁 Estrutura do Projeto

```
playground_server_js/
├── main.js                   # Entry point — app Express + middlewares + error handler + seed
├── package.json              # Dependências (express, zod, winston, ...) — SQLite via `node:sqlite` built-in
├── README.md                 # Este arquivo
├── .gitignore
├── logs/                     # Logs rotacionados (criado em runtime)
├── database.db               # SQLite (criado em runtime)
└── src/
    ├── config.js             # Configurações (PORT, DATABASE_PATH, admin defaults)
    ├── database.js           # Conexão node:sqlite (DatabaseSync) + DDL (initDb) + helper transaction()
    ├── logging.js            # Winston (console + arquivos rotacionados) + maskApiKey
    ├── errors.js             # Classe HttpError
    ├── auth.js               # Middlewares requireAuth e requireRole
    ├── validate.js           # Middleware genérico de validação zod
    ├── schemas.js            # Schemas zod (User/Item/Sale + paginação + IdParam)
    ├── routes/               # Express routers
    │   ├── users.js
    │   ├── items.js
    │   └── sales.js
    └── services/             # Lógica de negócio (SQL direto)
        ├── users.js
        ├── items.js
        └── sales.js
```

## 🚦 Rate Limiting

Implementado com **express-rate-limit**. Limite de **60 requisições por minuto por API key**.

- Requisições sem API key são limitadas por **IP**.
- `/` e `/health` são isentos.
- Ao exceder o limite, retorna **429** com header `Retry-After: 60`:

```json
{"detail": "Rate limit exceeded: 60 per 1 minute. Try again in a minute."}
```

## 📝 Logging

Toda request e todo erro é logado via **winston**, com rotação diária em `logs/`.

- **Identidade nos logs:** email do usuário autenticado (nunca a API key).
- **Formato de request:** `METHOD PATH -> STATUS | user=<email|anonymous> | elapsed=Xms`
- **Níveis:** 2xx/3xx → info, 4xx → warn, 5xx → error.
- **Sinks:** console + `logs/app-*.log` (info+, rotação 10 MB, retenção 14 dias, zip) + `logs/error-*.log` (error+, retenção 30 dias, zip).
- **Error handler global:** captura `HttpError` (resposta `{detail}` com status do erro) e exceções não tratadas (traceback completo em `error-*.log`, resposta genérica 500 ao cliente).

A API Key nunca é escrita em arquivo. Apenas a forma mascarada `****last4` aparece em logs informativos (seed do admin, rate limit, por exemplo).

## 🗄️ Modelo de Dados

### users
| Coluna   | Tipo    | Descrição                              |
|----------|---------|----------------------------------------|
| id       | INTEGER | Chave primária (autoincrement)         |
| name     | TEXT    | Nome do usuário                        |
| email    | TEXT    | Email único                            |
| role     | TEXT    | admin, manager, seller ou viewer       |
| api_key  | TEXT    | UUID gerado automaticamente            |
| active   | INTEGER | 0/1 (default: 1)                       |

### items
| Coluna      | Tipo    | Descrição                    |
|-------------|---------|------------------------------|
| id          | INTEGER | Chave primária               |
| name        | TEXT    | Nome do item                 |
| description | TEXT    | Descrição (opcional)         |
| price       | REAL    | Preço unitário               |
| quantity    | INTEGER | Quantidade em estoque        |

### sales
| Coluna     | Tipo    | Descrição                                    |
|------------|---------|----------------------------------------------|
| id         | INTEGER | Chave primária                               |
| user_id    | INTEGER | FK → users.id (quem vendeu) — **indexado**   |
| item_id    | INTEGER | FK → items.id (item vendido) — **indexado**  |
| quantity   | INTEGER | Quantidade vendida                           |
| unit_price | REAL    | Preço no momento da venda                    |
| total      | REAL    | Total (quantity × unit_price, 2 casas)       |
| created_at | TEXT    | Timestamp da venda (UTC) — **indexado**      |

> Os índices (`ix_sales_user_id`, `ix_sales_item_id`, `ix_sales_created_at`) são criados com `CREATE INDEX IF NOT EXISTS` no boot, então funcionam em bases existentes.

## 🧩 Diferenças vs. versão Python (`playground_server_py`)

| Aspecto              | py                              | js                                       |
|----------------------|---------------------------------|------------------------------------------|
| Framework            | FastAPI                         | Express                                  |
| Validação            | Pydantic                        | zod                                      |
| ORM/DB driver        | SQLAlchemy                      | `node:sqlite` built-in (SQL direto, síncrono) |
| Logging              | loguru                          | winston + winston-daily-rotate-file      |
| Rate limit           | slowapi                         | express-rate-limit                       |
| OpenAPI/Swagger      | ✅ (`/docs`, `/redoc`)          | ❌                                       |
| Boolean em SQLite    | `Boolean` (SQLAlchemy)          | `INTEGER` 0/1, convertido em `boolean`   |

Endpoints, schemas, regras de auth/role, validações e regras de estoque são **idênticos**.

## 🛠️ Requisitos

- Node.js **22+** (usa `node:sqlite` built-in; testado em 24.x). Em Node 22/23/24 sai `ExperimentalWarning` na inicialização — sem impacto funcional.
- Nenhuma build tool nativa necessária — todas as dependências são puro JS.
