from django.test import override_settings

from django_llm_optimizer.conf import DEFAULTS, get_settings


def test_default_settings_are_loaded():
    profiler_settings = get_settings()
    assert profiler_settings.enabled is True
    assert profiler_settings.capture_celery is True
    assert profiler_settings.capture_temporal is True
    assert profiler_settings.max_stack_frames == DEFAULTS["MAX_STACK_FRAMES"]
    assert str(profiler_settings.reports_directory) == DEFAULTS["REPORTS_PATH"]


@override_settings(DJANGO_LLM_PROFILER={"ENABLED": False, "MAX_STACK_FRAMES": 3})
def test_settings_override_defaults():
    profiler_settings = get_settings()
    assert profiler_settings.enabled is False
    assert profiler_settings.max_stack_frames == 3


@override_settings(DJANGO_LLM_PROFILER={"REPORTS_PATH": "tmp/profiler-reports"})
def test_reports_path_is_configurable():
    profiler_settings = get_settings()
    assert str(profiler_settings.reports_directory) == "tmp/profiler-reports"


@override_settings(DJANGO_LLM_PROFILER={"EXPORT_JSON_PATH": "tmp/legacy-export-path"})
def test_export_json_path_alias_still_works():
    profiler_settings = get_settings()
    assert str(profiler_settings.reports_directory) == "tmp/legacy-export-path"
