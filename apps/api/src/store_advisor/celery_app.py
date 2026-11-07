"""CLI import validates configuration, then exposes the shared worker instance."""

from store_advisor.worker import create_worker

app = create_worker()
