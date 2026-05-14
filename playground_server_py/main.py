import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION, ADMIN_EMAIL, ADMIN_NAME
from app.database import SessionLocal, init_db
from app.logging_config import configure_logging, mask_api_key
from app.models.user import User
from app.routers import items, sales, users

configure_logging()


def _rate_limit_key(request: Request) -> str:
    """Rate limit per API key; fall back to client IP for unauthenticated requests."""
    key = request.headers.get("x-api-key")
    if key:
        return key
    return request.client.host if request.client else "unknown"


limiter = Limiter(default_limits=["60/minute"], key_func=_rate_limit_key)


def seed_admin():
    """Create the admin user if it doesn't exist yet.

    On first creation, the api_key is printed ONCE to stdout so the operator can
    capture it. It is never written to the log files.
    """
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if admin:
            logger.info(
                "Admin already exists | email={} | api_key={}",
                admin.email,
                mask_api_key(admin.api_key),
            )
            return
        admin = User(name=ADMIN_NAME, email=ADMIN_EMAIL, role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(
            "Admin user created | email={} | api_key={}",
            admin.email,
            mask_api_key(admin.api_key),
        )
        # One-time display to operator; not logged.
        print(f"\n{'='*50}")
        print(f"  Usuário admin criado com sucesso!")
        print(f"  Email:   {admin.email}")
        print(f"  API Key: {admin.api_key}")
        print(f"  GUARDE ESTA API KEY!")
        print(f"{'='*50}\n")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app | title={} | version={}", APP_TITLE, APP_VERSION)
    init_db()
    seed_admin()
    yield
    logger.info("Shutting down app")


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter


def _custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Override slowapi default so 429 uses {"detail": ...} like the rest of the API."""
    key = _rate_limit_key(request)
    user_email = getattr(request.state, "user_email", "anonymous")
    logger.warning(
        "RateLimit exceeded | {} {} | key={} | user={} | limit={}",
        request.method,
        request.url.path,
        mask_api_key(key) if len(key) > 10 else key,
        user_email,
        exc.detail,
    )
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}. Try again in a minute."},
        headers={"Retry-After": "60"},
    )


# SlowAPIMiddleware catches RateLimitExceeded internally before FastAPI exception
# handlers run. Patch the module-level handler it references at call time.
import slowapi.middleware as _slowapi_middleware
_slowapi_middleware._rate_limit_exceeded_handler = _custom_rate_limit_handler

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    """Log every HTTP request. Identifies user by email (never API key)."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:  # bubbled up before handlers
        elapsed_ms = (time.perf_counter() - start) * 1000
        user_email = getattr(request.state, "user_email", "anonymous")
        logger.opt(exception=exc).error(
            "request failed | {} {} | user={} | elapsed={:.1f}ms",
            request.method,
            request.url.path,
            user_email,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    user_email = getattr(request.state, "user_email", "anonymous")
    log = logger.bind(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        user=user_email,
    )
    if response.status_code >= 500:
        log.error(
            "{} {} -> {} | user={} | elapsed={:.1f}ms",
            request.method,
            request.url.path,
            response.status_code,
            user_email,
            elapsed_ms,
        )
    elif response.status_code >= 400:
        log.warning(
            "{} {} -> {} | user={} | elapsed={:.1f}ms",
            request.method,
            request.url.path,
            response.status_code,
            user_email,
            elapsed_ms,
        )
    else:
        log.info(
            "{} {} -> {} | user={} | elapsed={:.1f}ms",
            request.method,
            request.url.path,
            response.status_code,
            user_email,
            elapsed_ms,
        )
    return response



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    user_email = getattr(request.state, "user_email", "anonymous")
    logger.warning(
        "HTTPException | {} {} | status={} | detail={} | user={}",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
        user_email,
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    user_email = getattr(request.state, "user_email", "anonymous")
    logger.warning(
        "ValidationError | {} {} | user={} | errors={}",
        request.method,
        request.url.path,
        user_email,
        exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    user_email = getattr(request.state, "user_email", "anonymous")
    logger.opt(exception=exc).error(
        "Unhandled exception | {} {} | user={}",
        request.method,
        request.url.path,
        user_email,
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal Server Error"}
    )


app.include_router(users.router)
app.include_router(items.router)
app.include_router(sales.router)


@app.get("/", tags=["Root"])
@limiter.exempt
def root():
    return {"message": "REST Server ativo. Acesse /docs para a documentação."}


@app.get("/health", tags=["Root"])
@limiter.exempt
def health():
    return {"status": "ok"}
