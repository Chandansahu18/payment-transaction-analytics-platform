from __future__ import annotations
import argparse
import asyncio
import ctypes
import os
import sys
from typing import Any
from prefect.client.schemas.schedules import CronSchedule
from orchestration.config import bootstrap_env
from orchestration.pipeline_flow import payment_analytics_pipeline

DEFAULT_TIMEZONE = "Asia/Kolkata"


def _use_windows_short_executable() -> None:

    if os.name != "nt" or " " not in sys.executable:
        return
    buffer = ctypes.create_unicode_buffer(32768)
    if ctypes.windll.kernel32.GetShortPathNameW(sys.executable, buffer, len(buffer)):
        sys.executable = buffer.value

def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the payment analytics Prefect deployment")
    parser.add_argument("--cron", default=None, help='Cron schedule in local TZ, e.g. "35 0 * * *"')
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help=f'Cron timezone - clock region for schedule times (default: {DEFAULT_TIMEZONE} = India IST)',
    )
    parser.add_argument("--name", default="payment-analytics-pipeline")
    args = parser.parse_args()

    bootstrap_env()
    _use_windows_short_executable()

    serve_kwargs: dict[str, Any] = {
        "name": args.name,
        "tags": ["payment-analytics"],
    }
    if args.cron:
        serve_kwargs["schedule"] = CronSchedule(cron=args.cron, timezone=args.timezone)

    asyncio.run(payment_analytics_pipeline.serve(**serve_kwargs))


if __name__ == "__main__":
    main()