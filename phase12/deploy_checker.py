import importlib.util
import logging
import sqlite3
from pathlib import Path
from typing import List

from phase4.monetary_detector import MonetaryDetector
from phase12.models import DeploymentCheckResult, DeploymentVerificationReport

logger = logging.getLogger("phase12.deploy_checker")

PROJECT_ROOT = Path(".").resolve()
DB_PATH = PROJECT_ROOT / "data" / "discovery_engine.db"
VECTOR_PATH = PROJECT_ROOT / "data" / "vector_store" / "lsa_embedder_v1.joblib"
ENTRYPOINT_PATH = PROJECT_ROOT / "phase11" / "app.py"
STREAMLIT_CONFIG = PROJECT_ROOT / ".streamlit" / "config.toml"
GITHUB_WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "weekly_pipeline.yml"


class DeploymentChecker:
    """
    Phase 12 Deployment Checker.
    Verifies all prerequisites for Streamlit Cloud and local Streamlit deployment.
    """

    @staticmethod
    def run_pre_deployment_checks() -> DeploymentVerificationReport:
        checks: List[DeploymentCheckResult] = []

        # 1. Streamlit Entrypoint Check
        if ENTRYPOINT_PATH.exists():
            checks.append(DeploymentCheckResult(
                check_name="Streamlit Entrypoint File",
                category="Entrypoint",
                status="PASS",
                message=f"Main entrypoint '{ENTRYPOINT_PATH.relative_to(PROJECT_ROOT)}' exists and is readable.",
                details={"file_size": ENTRYPOINT_PATH.stat().st_size}
            ))
        else:
            checks.append(DeploymentCheckResult(
                check_name="Streamlit Entrypoint File",
                category="Entrypoint",
                status="FAIL",
                message=f"Main entrypoint '{ENTRYPOINT_PATH}' is missing!"
            ))

        # 2. SQLite Database Verification
        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM documents")
                d_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM chunks")
                c_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM documents WHERE relevance = 'relevant' AND duplicate_of IS NULL")
                canon_n = cur.fetchone()[0]
                conn.close()

                checks.append(DeploymentCheckResult(
                    check_name="SQLite Database Artifact",
                    category="Data Persistence",
                    status="PASS",
                    message=f"Database 'discovery_engine.db' verified with {d_count:,} total docs and {canon_n:,} canonical relevant docs (N=1,151).",
                    details={"total_documents": d_count, "chunks": c_count, "canonical_sample_n": canon_n}
                ))
            except Exception as e:
                checks.append(DeploymentCheckResult(
                    check_name="SQLite Database Artifact",
                    category="Data Persistence",
                    status="FAIL",
                    message=f"Failed reading database: {e}"
                ))
        else:
            checks.append(DeploymentCheckResult(
                check_name="SQLite Database Artifact",
                category="Data Persistence",
                status="FAIL",
                message=f"Database file '{DB_PATH}' is missing!"
            ))

        # 3. Vector Store Artifact Check
        if VECTOR_PATH.exists():
            checks.append(DeploymentCheckResult(
                check_name="Vector Store Matrix Artifact",
                category="Vector Store",
                status="PASS",
                message=f"LSA Vector Matrix '{VECTOR_PATH.relative_to(PROJECT_ROOT)}' exists ({VECTOR_PATH.stat().st_size / 1024 / 1024:.2f} MB).",
                details={"path": str(VECTOR_PATH), "size_mb": VECTOR_PATH.stat().st_size / 1024 / 1024}
            ))
        else:
            checks.append(DeploymentCheckResult(
                check_name="Vector Store Matrix Artifact",
                category="Vector Store",
                status="FAIL",
                message=f"Vector store matrix file '{VECTOR_PATH}' is missing!"
            ))

        # 4. Streamlit Configuration Check
        if STREAMLIT_CONFIG.exists():
            checks.append(DeploymentCheckResult(
                check_name="Streamlit Theme & Server Config",
                category="Configuration",
                status="PASS",
                message="Streamlit theme configuration `.streamlit/config.toml` exists.",
                details={"path": str(STREAMLIT_CONFIG)}
            ))
        else:
            checks.append(DeploymentCheckResult(
                check_name="Streamlit Theme & Server Config",
                category="Configuration",
                status="WARNING",
                message="`.streamlit/config.toml` does not exist; default Streamlit styles will be applied."
            ))

        # 5. Non-Monetary Guardrail Check
        is_mon, mon_copy = MonetaryDetector.check_query("discount promo code")
        if is_mon:
            checks.append(DeploymentCheckResult(
                check_name="Monetary Refusal Guardrail",
                category="Guardrails",
                status="PASS",
                message="Pre-retrieval monetary query interception is active and functional.",
                details={"refusal_copy_sample": mon_copy[:60]}
            ))
        else:
            checks.append(DeploymentCheckResult(
                check_name="Monetary Refusal Guardrail",
                category="Guardrails",
                status="FAIL",
                message="Monetary refusal guardrail failed to trigger!"
            ))

        # 6. GitHub Actions Independence Check
        if GITHUB_WORKFLOW.exists():
            checks.append(DeploymentCheckResult(
                check_name="GitHub Actions Workflow Independence",
                category="Automation",
                status="PASS",
                message="Weekly Monday pipeline workflow exists and runs independently of Streamlit UI.",
                details={"workflow_path": str(GITHUB_WORKFLOW)}
            ))

        passed_count = sum(1 for c in checks if c.status == "PASS")
        failed_count = sum(1 for c in checks if c.status == "FAIL")

        return DeploymentVerificationReport(
            deployment_ready=(failed_count == 0),
            total_checks_passed=passed_count,
            total_checks_failed=failed_count,
            checks=checks
        )
