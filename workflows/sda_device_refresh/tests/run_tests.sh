#!/usr/bin/env bash
# Run all unit tests for the sda_device_refresh rename_to_source_identity feature.
#
# Usage (from repo root):
#   bash workflows/sda_device_refresh/tests/run_tests.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCHEMA="workflows/sda_device_refresh/schema/sda_device_refresh_schema.yml"
FIXTURE_DIR="workflows/sda_device_refresh/tests/fixtures"

cd "$REPO_ROOT"

echo "============================================================"
echo " sda_device_refresh rename_to_source_identity – unit tests"
echo "============================================================"

# ── 1. Schema validation via yamale ─────────────────────────────
echo ""
echo "── Schema validation ────────────────────────────────────────"

PASS=0
FAIL=0

run_schema_test() {
    local label="$1"
    local fixture="$2"
    local expect_pass="$3"   # 'pass' or 'fail'

    if yamale -s "$SCHEMA" "$FIXTURE_DIR/$fixture" > /dev/null 2>&1; then
        result="pass"
    else
        result="fail"
    fi

    if [ "$result" = "$expect_pass" ]; then
        echo "  [PASS] $label"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $label (expected=$expect_pass, got=$result)"
        FAIL=$((FAIL + 1))
    fi
}

run_schema_test "valid: rename_to_source_identity with default loopback" \
    "valid_rename_with_defaults.yml" "pass"

run_schema_test "valid: rename_to_source_identity with target_loopback_ip override" \
    "valid_rename_with_loopback_override.yml" "pass"

run_schema_test "valid: no rename fields (backward compatibility)" \
    "valid_no_rename_backward_compat.yml" "pass"

echo ""
echo "  Schema results: $PASS passed, $FAIL failed"

# ── 2. Python Jinja2 logic unit tests ───────────────────────────
echo ""
echo "── Python unit tests (Jinja2 logic) ─────────────────────────"

python3 -m pytest \
    "$REPO_ROOT/workflows/sda_device_refresh/tests/unit/test_rename_logic.py" \
    -v --tb=short

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "============================================================"
if [ "$FAIL" -gt 0 ]; then
    echo " Schema validation: $FAIL FAILURE(S)"
    exit 1
else
    echo " All tests completed."
fi
