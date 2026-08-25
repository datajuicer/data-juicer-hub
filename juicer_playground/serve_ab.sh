#!/bin/bash
# ─────────────────────────────────────────────────
# Juicer AB comparison launcher — dual service on one host (optional)
#   Juicer     -> GPU 0, port 8000, served-name "juicer"
#   base model -> GPU 1, port 8001, served-name "raw"
# Used by the "AB Comparison" tab to visually compare both models on the same recipe.
# ─────────────────────────────────────────────────
# Usage:
#   bash serve_ab.sh --juicer /path/to/juicer-checkpoint --raw /path/to/Qwen3.6-35B-A3B
#   bash serve_ab.sh --stop
#   bash serve_ab.sh --help
# ─────────────────────────────────────────────────

set -euo pipefail

JUICER_PATH="${JUICER_PATH:-/path/to/juicer-checkpoint}"
RAW_PATH="${RAW_PATH:-/path/to/Qwen3.6-35B-A3B}"
JUICER_PORT=8000
RAW_PORT=8001
JUICER_GPUS="${JUICER_GPUS:-0}"
RAW_GPUS="${RAW_GPUS:-1}"
GPU_MEM_UTIL=0.90
MAX_MODEL_LEN=32768
# Hybrid GDN/Mamba arch: each decode seq needs one Mamba cache block; on a
# single 96G card only ~811 blocks fit, so the vLLM default (1024) aborts startup.
MAX_NUM_SEQS=256
REASONING_PARSER="qwen3"
GDN_PREFILL_BACKEND="${GDN_PREFILL_BACKEND:-}"
MOE_BACKEND="${MOE_BACKEND:-}"
ENFORCE_EAGER="${ENFORCE_EAGER:-false}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/vllm"
RAW_PID_FILE="${SCRIPT_DIR}/.vllm_raw.pid"
JUICER_PID_FILE="${SCRIPT_DIR}/.vllm_juicer.pid"

do_stop() {
    local exit_code="${1:-0}"
    local -a pids=()
    for pf in "$RAW_PID_FILE" "$JUICER_PID_FILE"; do
        if [ -f "$pf" ]; then
            PID=$(cat "$pf")
            if [[ "$PID" =~ ^[0-9]+$ ]] && kill -0 "$PID" 2>/dev/null; then
                echo "[AB] Stopping PID $PID ($(basename "$pf"))..."
                # launch() uses setsid, so terminate the whole vLLM process group,
                # including EngineCore and any active JIT compiler children.
                kill -TERM -- "-$PID" 2>/dev/null || true
                pids+=("$PID")
            fi
            rm -f "$pf"
        fi
    done
    # Wait for both services concurrently, so dual-service shutdown takes at
    # most 30 seconds rather than up to 30 seconds per service.
    for _ in $(seq 1 30); do
        local any_alive=false
        for PID in "${pids[@]}"; do
            kill -0 "$PID" 2>/dev/null && any_alive=true
        done
        [ "$any_alive" = false ] && break
        sleep 1
    done
    for PID in "${pids[@]}"; do
        kill -0 "$PID" 2>/dev/null && kill -KILL -- "-$PID" 2>/dev/null || true
    done
    echo "[AB] Stopped."
    exit "$exit_code"
}

STOP_MODE=false
while [ $# -gt 0 ]; do
    case "$1" in
        --raw)      RAW_PATH="$2"; shift 2 ;;
        --juicer)   JUICER_PATH="$2"; shift 2 ;;
        --raw-gpus) RAW_GPUS="$2"; shift 2 ;;
        --juicer-gpus) JUICER_GPUS="$2"; shift 2 ;;
        --stop)     STOP_MODE=true; shift ;;
        --juicer-port) JUICER_PORT="$2"; shift 2 ;;
        --raw-port) RAW_PORT="$2"; shift 2 ;;
        --gdn-prefill-backend) GDN_PREFILL_BACKEND="$2"; shift 2 ;;
        --moe-backend) MOE_BACKEND="$2"; shift 2 ;;
        --enforce-eager) ENFORCE_EAGER=true; shift ;;
        --no-enforce-eager) ENFORCE_EAGER=false; shift ;;
        --help|-h)
            echo "Usage: bash $0 --juicer PATH --raw PATH [OPTIONS]"
            echo "  --juicer PATH     Juicer model path (served-name: juicer, port $JUICER_PORT)"
            echo "  --raw PATH        Base model path (served-name: raw, port $RAW_PORT)"
            echo "  --juicer-gpus IDS Comma-separated devices for Juicer (default $JUICER_GPUS)"
            echo "  --raw-gpus IDS    Comma-separated devices for the base model (default $RAW_GPUS)"
            echo "  --juicer-port N   Juicer API port (default $JUICER_PORT)"
            echo "  --raw-port N      Base-model API port (default $RAW_PORT)"
            echo "  --gdn-prefill-backend NAME  GDN prefill backend (default: vLLM auto)"
            echo "  --moe-backend NAME  MoE kernel backend (default: vLLM auto)"
            echo "  --enforce-eager   Disable torch.compile and CUDA Graphs"
            echo "  --no-enforce-eager  Keep compiled/CUDA Graph mode (default)"
            echo "  --stop            Stop both services"
            exit 0 ;;
        -*) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

[ "$STOP_MODE" = true ] && do_stop

for p in "$RAW_PATH" "$JUICER_PATH"; do
    if [ ! -d "$p" ]; then echo "[ERROR] Model path does not exist: $p"; exit 1; fi
done
for pf in "$RAW_PID_FILE" "$JUICER_PID_FILE"; do
    if [ -f "$pf" ]; then
        PID=$(cat "$pf")
        if [[ "$PID" =~ ^[0-9]+$ ]] && kill -0 "$PID" 2>/dev/null; then
            echo "[ERROR] A service is already running (PID $PID). Run: bash $0 --stop" >&2
            exit 1
        fi
        rm -f "$pf"
    fi
done
for port in "$JUICER_PORT" "$RAW_PORT"; do
    if [[ ! "$port" =~ ^[0-9]+$ ]] || (( 10#$port < 1 || 10#$port > 65535 )); then
        echo "[ERROR] Invalid TCP port: $port" >&2
        exit 1
    fi
done
if [ "$JUICER_PORT" = "$RAW_PORT" ]; then
    echo "[ERROR] Juicer and raw must use different ports: $JUICER_PORT" >&2
    exit 1
fi
IFS=',' read -r -a juicer_gpu_ids <<< "$JUICER_GPUS"
IFS=',' read -r -a raw_gpu_ids <<< "$RAW_GPUS"
for gpu in "${juicer_gpu_ids[@]}" "${raw_gpu_ids[@]}"; do
    if [[ ! "$gpu" =~ ^[0-9]+$ ]]; then
        echo "[ERROR] Invalid GPU ID: $gpu" >&2
        exit 1
    fi
done
for juicer_gpu in "${juicer_gpu_ids[@]}"; do
    for raw_gpu in "${raw_gpu_ids[@]}"; do
        if [ "$juicer_gpu" = "$raw_gpu" ]; then
            echo "[ERROR] Juicer and raw GPU sets overlap on device $juicer_gpu" >&2
            exit 1
        fi
    done
done
if [[ -n "$GDN_PREFILL_BACKEND" && "$GDN_PREFILL_BACKEND" != "triton" && "$GDN_PREFILL_BACKEND" != "flashinfer" && "$GDN_PREFILL_BACKEND" != "cutedsl" ]]; then
    echo "[ERROR] Invalid GDN prefill backend: $GDN_PREFILL_BACKEND" >&2
    exit 1
fi
mkdir -p "$LOG_DIR"

launch() {
    local name="$1" path="$2" port="$3" gpus="$4" pidfile="$5" logfile="$6"
    local parallel_size
    local -a backend_args=() eager_args=()
    parallel_size=$(awk -F',' '{print NF}' <<<"$gpus")
    if [ "$ENFORCE_EAGER" = true ]; then
        eager_args+=(--enforce-eager)
    fi
    if [ -n "$GDN_PREFILL_BACKEND" ]; then
        backend_args+=(--gdn-prefill-backend "$GDN_PREFILL_BACKEND")
    fi
    if [ -n "$MOE_BACKEND" ]; then
        backend_args+=(--moe-backend "$MOE_BACKEND")
    fi
    echo "[AB] Launching $name  gpus=$gpus port=$port"
    # Per-service FlashInfer JIT workspace: both models share the same arch, and
    # two concurrent ninja builds in one cache dir kill each other (exit 130).
    # setsid: detach from the terminal's process group so Ctrl+C on this script
    # cannot SIGINT the servers or their ninja/JIT children.
    CUDA_VISIBLE_DEVICES="$gpus" VLLM_ENGINE_READY_TIMEOUT_S=18000 \
        FLASHINFER_WORKSPACE_BASE="${HOME}/.cache/flashinfer-${name}" \
        setsid nohup \
        python -m vllm.entrypoints.openai.api_server \
        --model "$path" --served-model-name "$name" \
        --host 0.0.0.0 --port "$port" \
        --tensor-parallel-size "$parallel_size" \
        --gpu-memory-utilization "$GPU_MEM_UTIL" \
        --max-model-len "$MAX_MODEL_LEN" \
        --max-num-seqs "$MAX_NUM_SEQS" \
        "${backend_args[@]}" \
        "${eager_args[@]}" \
        --trust-remote-code --dtype auto --language-model-only \
        --reasoning-parser "$REASONING_PARSER" \
        > "$logfile" 2>&1 &
    echo "$!" > "$pidfile"
    echo "[AB] $name started (PID $!), log: $logfile"
}

wait_ready() {
    local name="$1" port="$2" pidfile="$3"
    local pid; pid=$(cat "$pidfile")
    local start; start=$(date +%s)
    while true; do
        if ! kill -0 "$pid" 2>/dev/null; then echo "[ERROR] $name exited early, see log"; return 1; fi
        if curl -sf "http://localhost:${port}/health" >/dev/null 2>&1; then
            echo "[AB] $name READY on :$port ($(( $(date +%s) - start ))s)"; return 0
        fi
        [ $(( $(date +%s) - start )) -gt 18000 ] && { echo "[ERROR] $name timeout"; return 1; }
        sleep 5
    done
}

launch juicer "$JUICER_PATH" "$JUICER_PORT" "$JUICER_GPUS" "$JUICER_PID_FILE" "$LOG_DIR/vllm_juicer.log"
launch raw "$RAW_PATH" "$RAW_PORT" "$RAW_GPUS" "$RAW_PID_FILE" "$LOG_DIR/vllm_raw.log"

echo ""
echo "============================================================"
echo "  Juicer AB dual-service starting"
echo "    juicer -> :$JUICER_PORT  (device $JUICER_GPUS)"
echo "    raw    -> :$RAW_PORT  (device $RAW_GPUS)"
echo "    GDN prefill backend: ${GDN_PREFILL_BACKEND:-vLLM auto}"
echo "    MoE backend: ${MOE_BACKEND:-vLLM auto}"
echo "    Eager execution: $ENFORCE_EAGER"
echo "============================================================"
echo ""

wait_ready juicer "$JUICER_PORT" "$JUICER_PID_FILE" &
W1=$!
wait_ready raw "$RAW_PORT" "$RAW_PID_FILE" &
W2=$!
WAIT_STATUS=0
wait "$W1" || WAIT_STATUS=1
wait "$W2" || WAIT_STATUS=1
if [ "$WAIT_STATUS" -ne 0 ]; then
    echo "[ERROR] AB startup failed; stopping both services." >&2
    do_stop 1
fi

echo ""
echo "[AB] Both services ready. Frontend setup:"
echo "    export JUICER_BASE_URL=http://localhost:${JUICER_PORT}/v1"
echo "    export JUICER_RAW_BASE_URL=http://localhost:${RAW_PORT}/v1"
echo "    python app.py   # open http://localhost:7860 -> AB Comparison tab"
echo ""
echo "Stop: bash $0 --stop"
