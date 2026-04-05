#!/bin/bash
# ============================================================
# Sandbox Persistence Test — Generic Version
# ============================================================
# Purpose: Detect whether a cloud sandbox persists across sessions.
#
# Usage:
#   bash run_test.sh              # Run test (compare with baseline)
#   bash run_test.sh --baseline   # First run on this platform: record baseline
#
# Files in same directory:
#   baseline.env  — auto-generated, platform-scoped snapshot
# ============================================================

EXP_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKER_DIR="/tmp"

detect_env() {
    local cid=""
    [ -n "$FC_CONTAINER_ID" ] && cid="$FC_CONTAINER_ID"
    [ -z "$cid" ] && [ -f /proc/self/cgroup ] && cid=$(head -1 /proc/self/cgroup 2>/dev/null | grep -oE '[0-9a-f]{8,}' | tail -1)
    [ -z "$cid" ] && cid="unknown"

    local uptime=""
    if [ -f /proc/uptime ]; then
        uptime=$(awk '{printf "%.0f", $1}' /proc/uptime)
    else
        uptime="unknown"
    fi

    local hostname_val=$(hostname 2>/dev/null || echo "unknown")

    local os="unknown"
    [ -f /etc/os-release ] && os=$(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)

    local platform="unknown"
    [ -n "$FC_FUNCTION_NAME" ] && platform="aliyun-fc"
    [ -n "$AWS_LAMBDA_FUNCTION_NAME" ] && platform="aws-lambda"
    [ -n "$FUNCTION_NAME" ] && platform="gcp-cloud-function"
    [ -n "$VERCEL" ] && platform="vercel"
    [ -n "$KATA_CONTAINER" ] && platform="$platform+kata"

    # Platform fingerprint: hostname + platform + OS (used to detect platform switches)
    local fingerprint="${hostname_val}|${platform}|${os}"

    local ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    local epoch=$(date +%s 2>/dev/null || echo "0")

    echo "CONTAINER_ID=$cid"
    echo "UPTIME_SECONDS=$uptime"
    echo "HOSTNAME=$hostname_val"
    echo "OS=$os"
    echo "PLATFORM=$platform"
    echo "PLATFORM_FINGERPRINT=$fingerprint"
    echo "TIMESTAMP=$ts"
    echo "EPOCH=$epoch"
}

get_baseline_file() {
    # Derive a platform-specific baseline filename from current fingerprint
    local fp=$(detect_env | grep PLATFORM_FINGERPRINT | cut -d= -f2)
    # Hash the fingerprint to get a safe filename
    local hash=$(echo "$fp" | md5sum 2>/dev/null | cut -c1-12 || echo "default")
    echo "$EXP_DIR/baseline-${hash}.env"
}

get_current_fingerprint() {
    detect_env | grep PLATFORM_FINGERPRINT | cut -d= -f2
}

get_existing_baselines() {
    ls "$EXP_DIR"/baseline-*.env 2>/dev/null
}

write_markers() {
    echo "alive at $(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$MARKER_DIR/vik_heartbeat.txt"

    local count=0
    [ -f "$MARKER_DIR/vik_counter.txt" ] && count=$(cat "$MARKER_DIR/vik_counter.txt")
    count=$((count + 1))
    echo "$count" > "$MARKER_DIR/vik_counter.txt"

    local cid=$(detect_env | grep CONTAINER_ID | cut -d= -f2)
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') count=$count container=$cid" >> "$MARKER_DIR/vik_counter_log.txt" 2>/dev/null
    echo "Markers written. Counter: $count"
}

check_markers() {
    echo ""
    echo "--- /tmp Marker Files ---"
    if [ -f "$MARKER_DIR/vik_heartbeat.txt" ]; then
        echo "HEARTBEAT: FOUND"
        echo "  Content: $(cat "$MARKER_DIR/vik_heartbeat.txt")"
    else
        echo "HEARTBEAT: NOT FOUND (disk was reset)"
    fi

    if [ -f "$MARKER_DIR/vik_counter.txt" ]; then
        echo "COUNTER: FOUND"
        echo "  Value: $(cat "$MARKER_DIR/vik_counter.txt")"
    else
        echo "COUNTER: NOT FOUND (disk was reset)"
    fi

    if [ -f "$MARKER_DIR/vik_counter_log.txt" ]; then
        echo "COUNTER_LOG: FOUND"
        cat "$MARKER_DIR/vik_counter_log.txt"
    else
        echo "COUNTER_LOG: NOT FOUND"
    fi
}

compare_with_baseline() {
    local baseline_file="$1"
    echo ""
    echo "--- Comparison with Baseline ---"

    # Parse current values into a temp file (avoid eval on values with special chars)
    local current_env_file
    current_env_file=$(mktemp)
    detect_env > "$current_env_file"

    # Parse values safely using grep/cut instead of eval
    get_val() {
        local file="$1" key="$2"
        grep "^${key}=" "$file" | cut -d'=' -f2-
    }

    # Parse baseline values safely
    local CONTAINER_ID UPTIME_SECONDS HOSTNAME OS PLATFORM PLATFORM_FINGERPRINT TIMESTAMP EPOCH
    CONTAINER_ID=$(get_val "$current_env_file" CONTAINER_ID)
    UPTIME_SECONDS=$(get_val "$current_env_file" UPTIME_SECONDS)
    HOSTNAME=$(get_val "$current_env_file" HOSTNAME)
    OS=$(get_val "$current_env_file" OS)
    PLATFORM=$(get_val "$current_env_file" PLATFORM)
    PLATFORM_FINGERPRINT=$(get_val "$current_env_file" PLATFORM_FINGERPRINT)
    TIMESTAMP=$(get_val "$current_env_file" TIMESTAMP)
    EPOCH=$(get_val "$current_env_file" EPOCH)

    local BASELINE_CONTAINER_ID BASELINE_UPTIME_SECONDS BASELINE_HOSTNAME BASELINE_OS
    local BASELINE_PLATFORM BASELINE_PLATFORM_FINGERPRINT BASELINE_TIMESTAMP BASELINE_EPOCH
    BASELINE_CONTAINER_ID=$(get_val "$baseline_file" CONTAINER_ID)
    BASELINE_UPTIME_SECONDS=$(get_val "$baseline_file" UPTIME_SECONDS)
    BASELINE_HOSTNAME=$(get_val "$baseline_file" HOSTNAME)
    BASELINE_OS=$(get_val "$baseline_file" OS)
    BASELINE_PLATFORM=$(get_val "$baseline_file" PLATFORM)
    BASELINE_PLATFORM_FINGERPRINT=$(get_val "$baseline_file" PLATFORM_FINGERPRINT)
    BASELINE_TIMESTAMP=$(get_val "$baseline_file" TIMESTAMP)
    BASELINE_EPOCH=$(get_val "$baseline_file" EPOCH)

    # Platform switch detection
    if [ "$PLATFORM_FINGERPRINT" != "$BASELINE_PLATFORM_FINGERPRINT" ]; then
        echo "⚠ PLATFORM CHANGED"
        echo "  Baseline: $BASELINE_PLATFORM_FINGERPRINT"
        echo "  Current:  $PLATFORM_FINGERPRINT"
        echo "  This is a DIFFERENT environment, not a container reset."
        echo "  Results below are NOT comparable. Run --baseline for this platform."
        return 1
    fi

    # Container ID comparison
    if [ "$CONTAINER_ID" = "$BASELINE_CONTAINER_ID" ]; then
        echo "CONTAINER_ID: UNCHANGED ($CONTAINER_ID) ✓"
    else
        echo "CONTAINER_ID: CHANGED ($BASELINE_CONTAINER_ID → $CONTAINER_ID)"
    fi

    # Time elapsed
    echo "BASELINE_EPOCH=$BASELINE_EPOCH"
    echo "CURRENT_EPOCH=$EPOCH"
    echo "ELAPSED=$(( EPOCH - BASELINE_EPOCH )) seconds ($(( (EPOCH - BASELINE_EPOCH) / 3600 )) hours)"

    # Cleanup temp file
    rm -f "$current_env_file"
}

# === Main ===
echo "============================================================"
echo " Sandbox Persistence Test"
echo " $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================"
echo ""
echo "--- Current Environment ---"
detect_env | grep -v PLATFORM_FINGERPRINT | while read line; do echo "  $line"; done

if [ "$1" = "--baseline" ]; then
    local_file=$(get_baseline_file)
    echo ""
    echo "--- Saving Baseline ---"
    detect_env > "$local_file"
    echo "Saved to: $local_file"
    write_markers
else
    # Find the baseline that matches current platform
    current_fp=$(get_current_fingerprint)
    matched_baseline=""
    for bf in $(get_existing_baselines); do
        bf_fp=$(grep PLATFORM_FINGERPRINT "$bf" 2>/dev/null | cut -d= -f2)
        if [ "$bf_fp" = "$current_fp" ]; then
            matched_baseline="$bf"
            break
        fi
    done

    check_markers

    if [ -n "$matched_baseline" ]; then
        echo ""
        echo "Found matching baseline: $matched_baseline"
        compare_with_baseline "$matched_baseline"
        echo ""
        echo "--- Updating Markers ---"
        write_markers
    else
        existing=$(get_existing_baselines)
        if [ -n "$existing" ]; then
            echo ""
            echo "⚠ No baseline found for this platform."
            echo "  Existing baselines from other platforms:"
            for bf in $existing; do
                bf_platform=$(grep PLATFORM "$bf" 2>/dev/null | cut -d= -f2)
                bf_hostname=$(grep HOSTNAME "$bf" 2>/dev/null | cut -d= -f2)
                bf_time=$(grep TIMESTAMP "$bf" 2>/dev/null | cut -d= -f2)
                echo "    - $(basename $bf): platform=$bf_platform host=$bf_hostname time=$bf_time"
            done
            echo ""
            echo "  Run --baseline to create one for this platform."
        else
            echo ""
            echo "⚠ No baseline found. Run with --baseline first."
        fi
    fi
fi

echo ""
echo "============================================================"
echo " Done"
echo "============================================================"
