# Playground Server — OxeTech RPA

Servidor REST modular construído com **FastAPI** + **SQLite** para prática de integrações de sistemas.

## 🚀 Quick Start

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd oxetech_rpa/playground_server

# 2. Instalar dependências (requer uv - https://docs.astral.sh/uv/)
uv sync

# 3. Rodar o servidor
uv run uvicorn main:app --reload --port 8000
```

Na primeira execução, o servidor cria automaticamente:
- O banco de dados SQLite (`database.db`)
- O diretório `logs/` com os arquivos `app.log` e `error.log` (rotacionados)
- Um usuário **admin** com uma **API Key** exibida no console **apenas uma vez** (na criação)

> ⚠️ **Guarde a API Key do admin!** Em execuções subsequentes apenas uma forma mascarada (`****last4`) aparece nos logs. A chave completa **nunca** é gravada em arquivo.

## 📖 Documentação Interativa

Com o servidor rodando, acesse:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health check**: [http://localhost:8000/health](http://localhost:8000/health) — sem autenticação

## 🔑 Autenticação

Toda requisição (exceto `/docs` e `/`) exige o header `X-API-Key`:

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

| Ação                      | admin | manager | seller | viewer |
|---------------------------|:-----:|:-------:|:------:|:------:|
| `GET /users`              | ✅    | ❌      | ❌     | ❌     |
| `POST /users`             | ✅    | ❌      | ❌     | ❌     |
| `PUT/PATCH/DELETE /users`  | ✅    | ❌      | ❌     | ❌     |
| `GET /items`              | ✅    | ✅      | ✅     | ✅     |
| `POST /items`             | ✅    | ✅      | ❌     | ❌     |
| `PUT/PATCH/DELETE /items`  | ✅    | ✅      | ❌     | ❌     |
| `GET /sales`              | ✅    | ✅      | ✅     | ✅     |
| `POST /sales`             | ✅    | ✅      | ✅     | ❌     |
| `PUT/PATCH/DELETE /sales`  | ✅    | ✅      | ❌     | ❌     |

## 📋 Endpoints

### Users (`/users`)

| Método   | Endpoint          | Descrição            | Role    |
|----------|-------------------|----------------------|---------|
| `GET`    | `/users`          | Listar usuários      | admin   |
| `GET`    | `/users/{id}`     | Buscar por ID        | admin   |
| `POST`   | `/users`          | Criar usuário        | admin   |
| `PUT`    | `/users/{id}`     | Atualizar completo   | admin   |
| `PATCH`  | `/users/{id}`     | Atualizar parcial    | admin   |
| `DELETE` | `/users/{id}`     | Remover              | admin   |

### Items (`/items`)

| Método   | Endpoint          | Descrição            | Role            |
|----------|-------------------|----------------------|-----------------|
| `GET`    | `/items`          | Listar itens         | todos           |
| `GET`    | `/items/{id}`     | Buscar por ID        | todos           |
| `POST`   | `/items`          | Criar item           | admin, manager  |
| `PUT`    | `/items/{id}`     | Atualizar completo   | admin, manager  |
| `PATCH`  | `/items/{id}`     | Atualizar parcial    | admin, manager  |
| `DELETE` | `/items/{id}`     | Remover              | admin, manager  |

### Sales (`/sales`)

| Método   | Endpoint          | Descrição            | Role                    |
|----------|-------------------|----------------------|-------------------------|
| `GET`    | `/sales`          | Listar vendas        | todos                   |
| `GET`    | `/sales/{id}`     | Buscar por ID        | todos                   |
| `POST`   | `/sales`          | Criar venda          | admin, manager, seller  |
| `PUT`    | `/sales/{id}`     | Atualizar completo   | admin, manager          |
| `PATCH`  | `/sales/{id}`     | Atualizar parcial    | admin, manager          |
| `DELETE` | `/sales/{id}`     | Remover              | admin, manager          |

> **Nota:** Ao criar uma venda, o estoque do item é decrementado automaticamente. Ao deletar, o estoque é restaurado.

## ✅ Validações de Schema

Entradas são validadas no schema Pydantic antes de chegar no service. Exemplos que retornam **422**:

- `price <= 0` ou `quantity < 0` em `Item`
- `quantity <= 0`, `quantity > 1_000_000` ou `item_id <= 0` em `Sale` (bloqueia venda negativa que aumentaria estoque)
- `email` mal formatado (`EmailStr`)
- `role` fora de `{admin, manager, seller, viewer}`
- `name` vazio

## 🧪 Exemplos com curl

### 1. Criar um usuário (seller)

```bash
curl -X POST http://localhost:8000/users \
  -H "X-API-Key: SUA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "João", "email": "joao@email.com", "role": "seller"}'
```

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
rest_server/
├── main.py                    # Entry point — app FastAPI + startup + middleware de log + exception handlers
├── pyproject.toml             # Dependências
├── README.md                  # Este arquivo
├── logs/                      # Logs rotacionados (app.log, error.log) — criado em runtime
├── app/
│   ├── config.py              # Configurações
│   ├── database.py            # Engine SQLAlchemy + session
│   ├── logging_config.py      # Config central do loguru (sinks + mask_api_key)
│   ├── models/                # Models SQLAlchemy (tabelas)
│   │   ├── user.py
│   │   ├── item.py
│   │   └── sale.py
│   ├── schemas/               # Pydantic schemas (request/response)
│   │   ├── user.py
│   │   ├── item.py
│   │   └── sale.py
│   ├── auth/                  # Autenticação e autorização
│   │   └── dependencies.py
│   ├── routers/               # Endpoints REST
│   │   ├── users.py
│   │   ├── items.py
│   │   └── sales.py
│   └── services/              # Lógica de negócio
│       ├── user_service.py
│       ├── item_service.py
│       └── sale_service.py
```

## 🚦 Rate Limiting

Todos os endpoints protegidos têm limite de **60 requisições por minuto por API key**.

- Requisições sem API key são limitadas por **IP**.
- `/`, `/health`, `/docs`, `/redoc` são isentos.
- Ao exceder o limite, retorna **429** com header `Retry-After: 60`:

```json
{"detail": "Rate limit exceeded: 60 per 1 minute. Try again in a minute."}
```

## 📝 Logging

Toda request e todo erro é logado via **loguru**, com rotação de arquivos em `logs/`.

- **Identidade nos logs:** email do usuário autenticado (nunca a API key).
- **Formato de request:** `METHOD PATH -> STATUS | user=<email|anonymous> | elapsed=Xms`
- **Níveis:** 2xx/3xx → INFO, 4xx → WARNING, 5xx → ERROR.
- **Sinks:** console (stderr) + `logs/app.log` (INFO+, rotação 10 MB, retenção 14 dias) + `logs/error.log` (ERROR+, retenção 30 dias).
- **Exception handlers globais:** `HTTPException`, `RequestValidationError` e exceções não tratadas (traceback completo em `error.log`, resposta genérica 500 para o cliente).

A API Key nunca é escrita em arquivo. Apenas a forma mascarada `****last4` aparece em logs informativos (seed do admin, por exemplo).

## 🗄️ Modelo de Dados

### users
| Coluna   | Tipo    | Descrição                              |
|----------|---------|----------------------------------------|
| id       | Integer | Chave primária (auto-increment)        |
| name     | String  | Nome do usuário                        |
| email    | String  | Email único                            |
| role     | String  | admin, manager, seller ou viewer       |
| api_key  | String  | UUID gerado automaticamente            |
| active   | Boolean | Se o usuário está ativo (default: true)|

### items
| Coluna      | Tipo    | Descrição                    |
|-------------|---------|------------------------------|
| id          | Integer | Chave primária               |
| name        | String  | Nome do item                 |
| description | Text    | Descrição (opcional)         |
| price       | Float   | Preço unitário               |
| quantity    | Integer | Quantidade em estoque        |

### sales
| Coluna     | Tipo     | Descrição                                    |
|------------|----------|----------------------------------------------|
| id         | Integer  | Chave primária                               |
| user_id    | Integer  | FK → users.id (quem vendeu) — **indexado**   |
| item_id    | Integer  | FK → items.id (item vendido) — **indexado**  |
| quantity   | Integer  | Quantidade vendida                           |
| unit_price | Float    | Preço no momento da venda                    |
| total      | Float    | Total (quantity × unit_price)                |
| created_at | DateTime | Timestamp da venda — **indexado**            |

> Se o arquivo SQLite já existia antes da adição dos índices, `create_all()` não altera a tabela. Para aplicar os índices, apague `database.db` em ambiente local ou crie os índices manualmente:
> ```sql
> CREATE INDEX ix_sales_user_id    ON sales(user_id);
> CREATE INDEX ix_sales_item_id    ON sales(item_id);
> CREATE INDEX ix_sales_created_at ON sales(created_at);
> ```
