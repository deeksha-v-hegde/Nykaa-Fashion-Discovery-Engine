import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from db.store import init_db
from api.routes_status import router as status_router
from api.routes_empty import router as empty_router
from api.routes_corpus import router as corpus_router
from api.routes_ask import router as ask_router
from api.routes_quant import router as quant_router
from api.routes_opps import router as opps_router
from phase8.routes_dashboard import router as dashboard_router
from phase10.routes_weekly import router as weekly_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nykaa_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=======================================================")
    logger.info(" Nykaa Fashion - AI Wishlist Discovery Engine")
    logger.info("=======================================================")
    init_db()
    logger.info(f" Environment: {settings.environment}")
    logger.info(f" Groq Configured: {settings.is_groq_configured}")
    if not settings.is_groq_configured:
        logger.warning(" [WARNING] GROQ_API_KEY is not set. Inference endpoints will report unconfigured.")
    else:
        logger.info(f" Active Groq Model: {settings.groq_model}")
    logger.info(f" Retrieval Strategy: {settings.retrieval_strategy} (Top-K: {settings.retrieval_top_k})")
    logger.info("=======================================================")
    yield
    logger.info("Shutting down Nykaa Discovery Engine.")


app = FastAPI(
    title="Nykaa Fashion — AI Wishlist Discovery Engine",
    description="Evidence-backed AI Product Discovery Engine for 30-day wishlist-to-purchase conversion.",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(status_router)
app.include_router(empty_router)
app.include_router(corpus_router)
app.include_router(ask_router)
app.include_router(quant_router)
app.include_router(opps_router)
app.include_router(dashboard_router)
app.include_router(weekly_router)

# Mount frontend build if available
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.host, port=settings.port, reload=True)
