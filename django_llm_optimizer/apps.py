from django.apps import AppConfig


class DjangoLlmProfilerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_llm_optimizer"
    verbose_name = "Django LLM Profiler"

    def ready(self) -> None:
        from .integrations.celery import maybe_setup_celery_signals

        maybe_setup_celery_signals()
