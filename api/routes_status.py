from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
import yaml

from config.settings import settings
from llm.groq_adapter import get_llm_provider

router = APIRouter(prefix="/api", tags=["System & Status"])


@router.get("/health")
def get_health() -> Dict[str, Any]:
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": "Nykaa Fashion AI Wishlist Discovery Engine",
        "phase": "Phase 0 - Foundation",
        "environment": settings.environment
    }


@router.get("/stack")
def get_stack() -> Dict[str, Any]:
    """
    Returns live runtime configuration for PM Chrome Stack Transparency panel.
    Shows 'Not configured' if env keys/models are missing without faking names.
    """
    return settings.get_stack_transparency()


@router.get("/sources")
def get_sources() -> Dict[str, Any]:
    """
    Returns registered public sources from source registry (Phase 0 seed).
    Labels Nykaa-specific vs broader fashion and automated vs manual.
    """
    sources_file = Path("config/sources.yaml")
    if not sources_file.exists():
        raise HTTPException(status_code=404, detail="sources.yaml not found")

    try:
        with open(sources_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            sources = data.get("sources", [])
            
        summary = {
            "total_sources": len(sources),
            "automated_count": sum(1 for s in sources if s.get("collection_mode") == "automated"),
            "manual_count": sum(1 for s in sources if s.get("collection_mode") == "manual_unavailable"),
            "nykaa_scope_count": sum(1 for s in sources if s.get("source_scope") == "nykaa"),
            "broader_scope_count": sum(1 for s in sources if s.get("source_scope") == "broader_fashion"),
            "sources": sources
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read sources: {str(e)}")


@router.get("/llm/ping")
def ping_llm() -> Dict[str, Any]:
    """Checks Groq adapter connectivity."""
    provider = get_llm_provider()
    return provider.ping()
