"""
UtilityGuard — Main pipeline that chains all agents together.

Usage:
  python pipeline.py --once       # Run one cycle
  python pipeline.py --schedule   # Run on 60-second loop
"""

import argparse
import json
import uuid
from datetime import datetime

from agents.perception_agent import PerceptionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.manager_agent import ManagerAgent
from logger_setup import get_agent_logger
from memory import memory
from sensor_data import inject_leak, inject_shortage, clear_anomalies, clear_anomaly

logger = get_agent_logger("Pipeline")

# ── Agent singletons ───────────────────────────────────────────────────────────

perception_agent = PerceptionAgent()
reasoning_agent = ReasoningAgent()
manager_agent = ManagerAgent()


def run_cycle() -> dict:
    """Run one full Perception → Reasoning → Manager cycle. Returns summary dict."""
    cycle_id = str(uuid.uuid4())[:8]
    logger.info(f"{'='*60}")
    logger.info(f"🔄 Starting cycle {cycle_id} at {datetime.utcnow().isoformat()}")
    logger.info(f"{'='*60}")

    try:
        # Step 1: Perception
        perceptions = perception_agent.run()

        # Step 2: Reasoning
        reasonings = reasoning_agent.run(perceptions)

        # Step 3: Manager orchestrates Action + Notification
        summary = manager_agent.run(perceptions, reasonings, cycle_id)

        logger.info(f"🏁 Cycle {cycle_id} finished — status: {summary.status}")
        return summary.model_dump()

    except Exception as e:
        logger.error(f"💥 Cycle {cycle_id} failed: {e}", exc_info=True)
        return {"cycle_id": cycle_id, "status": "failed", "error": str(e)}


def simulate_leak(zone_id: str = "zone_3") -> dict:
    """Inject a leak anomaly, run a cycle, then clear the anomaly."""
    logger.info(f"🧪 SIMULATION: Injecting LEAK into {zone_id}")
    inject_leak(zone_id)
    result = run_cycle()
    clear_anomaly(zone_id)
    logger.info(f"🧪 SIMULATION: Cleared anomaly for {zone_id}")
    return result


def simulate_shortage(zone_id: str = "zone_3") -> dict:
    """Inject a shortage anomaly, run a cycle, then clear the anomaly."""
    logger.info(f"🧪 SIMULATION: Injecting SHORTAGE into {zone_id}")
    inject_shortage(zone_id)
    result = run_cycle()
    clear_anomaly(zone_id)
    logger.info(f"🧪 SIMULATION: Cleared anomaly for {zone_id}")
    return result


def run_scheduled():
    """Run the pipeline on a 60-second interval using APScheduler."""
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()
    scheduler.add_job(run_cycle, "interval", seconds=60, id="utilityguard_cycle")
    logger.info("📅 Scheduled pipeline — running every 60 seconds (Ctrl+C to stop)")

    # Run once immediately
    run_cycle()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UtilityGuard Pipeline")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--schedule", action="store_true", help="Run on 60s loop")
    parser.add_argument("--simulate-leak", type=str, metavar="ZONE", help="Simulate leak")
    parser.add_argument("--simulate-shortage", type=str, metavar="ZONE", help="Simulate shortage")
    args = parser.parse_args()

    if args.simulate_leak:
        result = simulate_leak(args.simulate_leak)
        print(json.dumps(result, indent=2, default=str))
    elif args.simulate_shortage:
        result = simulate_shortage(args.simulate_shortage)
        print(json.dumps(result, indent=2, default=str))
    elif args.schedule:
        run_scheduled()
    else:
        result = run_cycle()
        print(json.dumps(result, indent=2, default=str))
