const { HttpError } = require("./errors");

function validate(schema, source) {
  return (req, res, next) => {
    const parsed = schema.safeParse(req[source]);
    if (!parsed.success) {
      return next(new HttpError(422, parsed.error.issues));
    }
    req[source] = parsed.data;
    next();
  };
}

module.exports = { validate };
