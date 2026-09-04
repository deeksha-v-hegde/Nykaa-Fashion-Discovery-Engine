"""
Local Scheduler Runner & Diagnostic Tool for Nykaa Discovery Engine
Simulates and tests the Weekly Monday research pipeline scheduler locally.
Usage:
    python -m phase10.scheduler_local          # Run a single scheduled pass immediately
    python -m phase10.scheduler_local --loop   # Run in continuous scheduler test mode
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone

from phase10.run_phase10 import run_phase10
from phase10.store import Phase10Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("local_scheduler")


def execute_scheduler_pass():
    logger.info("=================================================================")
    logger.info(" [LOCAL SCHEDULER] Triggering Scheduled Monday Research Pipeline Pass")
    logger.info("=================================================================")
    start_time = time.time()
    try:
        run_phase10()
        elapsed = time.time() - start_time
        logger.info(f" [LOCAL SCHEDULER] Pass completed successfully in {elapsed:.2f}s.")
        latest = Phase10Store.get_latest_weekly_run()
        if latest:
            logger.info(f" [LOCAL SCHEDULER] Latest Run ID: {latest.get('run_id')}")
            logger.info(f" [LOCAL SCHEDULER] Next Scheduled: {latest.get('next_scheduled_run')}")
            logger.info(f" [LOCAL SCHEDULER] Analysis Status: {latest.get('analysis_status', '').upper()}")
        return True
    except Exception as e:
        logger.error(f" [LOCAL SCHEDULER] Pipeline pass failed with error: {e}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="Nykaa Fashion Local Research Scheduler")
    parser.add_argument("--loop", action="store_true", help="Run in continuous periodic test loop")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds for loop mode (default: 60s)")
    args = parser.parse_args()

    if not args.loop:
        logger.info("Executing one-off local scheduler pass...")
        success = execute_scheduler_pass()
        sys.exit(0 if success else 1)
    else:
        logger.info(f"Starting continuous local scheduler test loop (Interval: {args.interval}s). Press Ctrl+C to stop.")
        iteration = 1
        try:
            while True:
                logger.info(f"\n--- Scheduler Iteration #{iteration} at {datetime.now(timezone.utc).isoformat()} ---")
                execute_scheduler_pass()
                iteration += 1
                logger.info(f"Sleeping for {args.interval} seconds before next cycle...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Local scheduler stopped by user.")


if __name__ == "__main__":
    main()
