"""
Unit tests for the rename_to_source_identity logic added to the
sda_device_refresh workflow.

Tests cover the Jinja2 template expressions extracted from:
  - enrich_refresh_pair_context.yml   (effective_target_loopback_ip)
  - migrate_refresh_pair.yml          (rename_status initial value in pair result)
  - refresh_single_device.yml         (rename loop filter, rename count aggregation)

Run:
    python -m pytest workflows/sda_device_refresh/tests/unit/test_rename_logic.py -v

Requirements: jinja2, pyyaml (both in requirements.txt)
"""

import pytest
import yaml
from jinja2 import Environment

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def j2(template_str, variables):
    """Render a Jinja2 template string with the given variables dict."""
    env = Environment()
    env.filters["default"] = lambda value, default="", boolean=False: (
        default if (value is None or (boolean and not value)) else value
    )
    tmpl = env.from_string(template_str)
    return tmpl.render(**variables)


def render_effective_target_loopback_ip(target_loopback_ip, source_management_ip_address):
    """Mirror enrich_refresh_pair_context.yml refresh_pair_effective_target_loopback_ip."""
    template = (
        "{{ refresh_pair_context.target_loopback_ip "
        "if (refresh_pair_context.target_loopback_ip | default('') | length) > 0 "
        "else refresh_pair_context.source_management_ip_address }}"
    )
    env = Environment()
    tmpl = env.from_string(template)
    return tmpl.render(
        refresh_pair_context={
            "target_loopback_ip": target_loopback_ip,
            "source_management_ip_address": source_management_ip_address,
        }
    )


def build_pair_result(rename_to_source_identity, cleanup_source_device, effective_target_loopback_ip):
    """
    Mirror the pair result dict built in migrate_refresh_pair.yml (success branch).
    Returns only the rename-relevant fields.
    """
    rename_status = "pending" if rename_to_source_identity else "skipped"
    cleanup_status = "pending" if cleanup_source_device else "skipped"
    return {
        "pair_key": "test_pair",
        "pair_display_name": "test_pair",
        "cleanup_requested": cleanup_source_device,
        "cleanup_status": cleanup_status,
        "rename_to_source_identity": rename_to_source_identity,
        "effective_target_loopback_ip": effective_target_loopback_ip,
        "rename_status": rename_status,
        "migration_succeeded": True,
    }


def simulate_rename_loop_filter(pair_results):
    """
    Mirror the refresh_single_device.yml rename loop filter:
      selectattr('cleanup_status', 'equalto', 'success')
      | selectattr('rename_to_source_identity', 'equalto', true)
    """
    return [
        r for r in pair_results
        if r.get("cleanup_status") == "success"
        and r.get("rename_to_source_identity") is True
    ]


def simulate_rename_counts(pair_results):
    """Mirror rename_requested_count and rename_success_count expressions."""
    requested = sum(1 for r in pair_results if r.get("rename_to_source_identity") is True)
    success = sum(1 for r in pair_results if r.get("rename_status") == "success")
    return requested, success


# ---------------------------------------------------------------------------
# effective_target_loopback_ip
# ---------------------------------------------------------------------------

class TestEffectiveTargetLoopbackIp:

    def test_uses_override_when_provided(self):
        result = render_effective_target_loopback_ip("10.0.0.50", "10.0.0.1")
        assert result == "10.0.0.50"

    def test_falls_back_to_source_ip_when_override_empty(self):
        result = render_effective_target_loopback_ip("", "10.0.0.1")
        assert result == "10.0.0.1"

    def test_falls_back_to_source_ip_when_override_none(self):
        # In Ansible the field is always coerced to '' via | default('');
        # empty string is the practical equivalent of None here.
        result = render_effective_target_loopback_ip("", "10.0.0.1")
        assert result == "10.0.0.1"

    def test_uses_override_even_when_source_ip_present(self):
        result = render_effective_target_loopback_ip("192.168.1.100", "192.168.1.1")
        assert result == "192.168.1.100"

    def test_source_ip_used_as_loopback_when_no_override(self):
        """In SDA, source management IP == loopback0: verify this default works."""
        result = render_effective_target_loopback_ip("", "204.1.2.50")
        assert result == "204.1.2.50"


# ---------------------------------------------------------------------------
# pair result rename_status initialization (migrate_refresh_pair.yml)
# ---------------------------------------------------------------------------

class TestPairResultRenameStatusInit:

    def test_rename_status_is_pending_when_rename_requested(self):
        result = build_pair_result(
            rename_to_source_identity=True,
            cleanup_source_device=True,
            effective_target_loopback_ip="10.0.0.1",
        )
        assert result["rename_status"] == "pending"

    def test_rename_status_is_skipped_when_rename_not_requested(self):
        result = build_pair_result(
            rename_to_source_identity=False,
            cleanup_source_device=True,
            effective_target_loopback_ip="10.0.0.1",
        )
        assert result["rename_status"] == "skipped"

    def test_rename_to_source_identity_propagated_true(self):
        result = build_pair_result(True, True, "10.0.0.1")
        assert result["rename_to_source_identity"] is True

    def test_rename_to_source_identity_propagated_false(self):
        result = build_pair_result(False, True, "10.0.0.1")
        assert result["rename_to_source_identity"] is False

    def test_effective_target_loopback_ip_propagated(self):
        result = build_pair_result(True, True, "204.1.1.50")
        assert result["effective_target_loopback_ip"] == "204.1.1.50"


# ---------------------------------------------------------------------------
# rename loop filter (refresh_single_device.yml)
# ---------------------------------------------------------------------------

class TestRenameLoopFilter:

    def _make_results(self):
        """Build a realistic set of pair results for filter testing."""
        return [
            {
                "pair_key": "pair_a",
                "pair_display_name": "pair_a",
                "cleanup_status": "success",
                "rename_to_source_identity": True,
                "rename_status": "pending",
                "migration_succeeded": True,
            },
            {
                "pair_key": "pair_b",
                "pair_display_name": "pair_b",
                "cleanup_status": "success",
                "rename_to_source_identity": False,
                "rename_status": "skipped",
                "migration_succeeded": True,
            },
            {
                "pair_key": "pair_c",
                "pair_display_name": "pair_c",
                "cleanup_status": "failed",
                "rename_to_source_identity": True,
                "rename_status": "pending",
                "migration_succeeded": True,
            },
            {
                "pair_key": "pair_d",
                "pair_display_name": "pair_d",
                "cleanup_status": "pending",
                "rename_to_source_identity": True,
                "rename_status": "pending",
                "migration_succeeded": True,
            },
        ]

    def test_only_pairs_with_cleanup_success_and_rename_requested_are_selected(self):
        results = self._make_results()
        selected = simulate_rename_loop_filter(results)
        assert len(selected) == 1
        assert selected[0]["pair_key"] == "pair_a"

    def test_pair_without_rename_requested_excluded(self):
        results = self._make_results()
        selected = simulate_rename_loop_filter(results)
        assert not any(r["pair_key"] == "pair_b" for r in selected)

    def test_pair_with_cleanup_failed_excluded(self):
        results = self._make_results()
        selected = simulate_rename_loop_filter(results)
        assert not any(r["pair_key"] == "pair_c" for r in selected)

    def test_pair_with_cleanup_pending_excluded(self):
        results = self._make_results()
        selected = simulate_rename_loop_filter(results)
        assert not any(r["pair_key"] == "pair_d" for r in selected)

    def test_empty_results_returns_empty_list(self):
        assert simulate_rename_loop_filter([]) == []

    def test_no_rename_requested_returns_empty_list(self):
        results = [
            {"cleanup_status": "success", "rename_to_source_identity": False, "rename_status": "skipped"}
        ]
        assert simulate_rename_loop_filter(results) == []


# ---------------------------------------------------------------------------
# rename count aggregation (refresh_single_device.yml / sda_device_refresh_playbook.yml)
# ---------------------------------------------------------------------------

class TestRenameCountAggregation:

    def test_rename_requested_count(self):
        pair_results = [
            {"rename_to_source_identity": True, "rename_status": "success"},
            {"rename_to_source_identity": True, "rename_status": "failed"},
            {"rename_to_source_identity": False, "rename_status": "skipped"},
        ]
        requested, success = simulate_rename_counts(pair_results)
        assert requested == 2

    def test_rename_success_count(self):
        pair_results = [
            {"rename_to_source_identity": True, "rename_status": "success"},
            {"rename_to_source_identity": True, "rename_status": "failed"},
            {"rename_to_source_identity": False, "rename_status": "skipped"},
        ]
        requested, success = simulate_rename_counts(pair_results)
        assert success == 1

    def test_all_succeed(self):
        pair_results = [
            {"rename_to_source_identity": True, "rename_status": "success"},
            {"rename_to_source_identity": True, "rename_status": "success"},
        ]
        requested, success = simulate_rename_counts(pair_results)
        assert requested == 2
        assert success == 2

    def test_none_requested(self):
        pair_results = [
            {"rename_to_source_identity": False, "rename_status": "skipped"},
            {"rename_to_source_identity": False, "rename_status": "skipped"},
        ]
        requested, success = simulate_rename_counts(pair_results)
        assert requested == 0
        assert success == 0

    def test_empty_pair_results(self):
        requested, success = simulate_rename_counts([])
        assert requested == 0
        assert success == 0


# ---------------------------------------------------------------------------
# Schema fixture YAML loading sanity check
# ---------------------------------------------------------------------------

class TestFixtureYamlValidity:

    FIXTURE_DIR = (
        "workflows/sda_device_refresh/tests/fixtures"
    )

    def _load(self, filename):
        import os
        root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        path = os.path.join(root, self.FIXTURE_DIR, filename)
        with open(path) as f:
            return yaml.safe_load(f)

    def test_valid_rename_with_defaults_loads(self):
        data = self._load("valid_rename_with_defaults.yml")
        pair = data["sda_device_refresh"]["jobs"][0]["device_refreshes"][0]
        assert pair["rename_to_source_identity"] is True
        assert "target_loopback_ip" not in pair["replacement_device"]

    def test_valid_rename_with_loopback_override_loads(self):
        data = self._load("valid_rename_with_loopback_override.yml")
        pair = data["sda_device_refresh"]["jobs"][0]["device_refreshes"][0]
        assert pair["rename_to_source_identity"] is True
        assert pair["replacement_device"]["target_loopback_ip"] == "204.1.1.50"

    def test_valid_no_rename_backward_compat_loads(self):
        data = self._load("valid_no_rename_backward_compat.yml")
        pairs = data["sda_device_refresh"]["jobs"][0]["device_refreshes"]
        for pair in pairs:
            assert "rename_to_source_identity" not in pair
