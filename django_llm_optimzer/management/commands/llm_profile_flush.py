from __future__ import annotations

from django.core.management.base import BaseCommand

from django_llm_optimzer.conf import get_storage


class Command(BaseCommand):
    help = "Clear stored django-llm-profiler traces."

    def handle(self, *args, **options):
        get_storage().clear()
        self.stdout.write("Cleared profiler traces.")
