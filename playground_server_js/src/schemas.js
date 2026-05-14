const { z } = require("zod");

const Role = z.enum(["admin", "manager", "seller", "viewer"]);

const UserCreate = z.object({
  name: z.string().min(1).max(120),
  email: z.string().email(),
  role: Role.default("viewer"),
});

const UserUpdate = z.object({
  name: z.string().min(1).max(120),
  email: z.string().email(),
  role: Role,
  active: z.boolean(),
});

const UserPatch = z
  .object({
    name: z.string().min(1).max(120).optional(),
    email: z.string().email().optional(),
    role: Role.optional(),
    active: z.boolean().optional(),
  })
  .strict();

const ItemCreate = z.object({
  name: z.string().min(1).max(200),
  description: z.string().max(2000).nullable().optional(),
  price: z.number().gt(0),
  quantity: z.number().int().gte(0).default(0),
});

const ItemUpdate = z.object({
  name: z.string().min(1).max(200),
  description: z.string().max(2000).nullable().optional(),
  price: z.number().gt(0),
  quantity: z.number().int().gte(0),
});

const ItemPatch = z
  .object({
    name: z.string().min(1).max(200).optional(),
    description: z.string().max(2000).nullable().optional(),
    price: z.number().gt(0).optional(),
    quantity: z.number().int().gte(0).optional(),
  })
  .strict();

const SaleCreate = z.object({
  item_id: z.number().int().gt(0),
  quantity: z.number().int().gt(0).lte(1_000_000),
});

const SaleUpdate = SaleCreate;

const SalePatch = z
  .object({
    item_id: z.number().int().gt(0).optional(),
    quantity: z.number().int().gt(0).lte(1_000_000).optional(),
  })
  .strict();

const Pagination = z.object({
  skip: z.coerce.number().int().gte(0).default(0),
  limit: z.coerce.number().int().gte(1).lte(100).default(100),
});

const IdParam = z.object({ id: z.coerce.number().int().gt(0) });

module.exports = {
  UserCreate,
  UserUpdate,
  UserPatch,
  ItemCreate,
  ItemUpdate,
  ItemPatch,
  SaleCreate,
  SaleUpdate,
  SalePatch,
  Pagination,
  IdParam,
};
