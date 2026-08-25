#!/bin/bash
# ─────────────────────────────────────────────────
# Juicer vLLM launcher — single-GPU service
# ─────────────────────────────────────────────────
# Usage:
#   bash serve.sh                              # default: start the Juicer model
#   bash serve.sh --model /path/to/model       # specify model path
#   bash serve.sh --stop                       # stop the running service
#   bash serve.sh --help                       # show help
# ─────────────────────────────────────────────────

set -euo pipefail

# ── Default config ──
MODEL_PATH="${MODEL_PATH:-/path/to/juicer-checkpoint}"
PORT=8000
GPU_MEM_UTIL=0.90
MAX_NUM_BATCHED_TOKENS=65536
MAX_NUM_SEQS=128
MAX_MODEL_LEN=32768
ENABLE_EP=false
REASONING_PARSER="qwen3"
GDN_PREFILL_BACKEND="${GDN_PREFILL_BACKEND:-}"
MOE_BACKEND="${MOE_BACKEND:-}"
ENFORCE_EAGER="${ENFORCE_EAGER:-false}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="${SCRIPT_DIR}/.vllm.pid"
LOG_DIR="${SCRIPT_DIR}/logs/vllm"
LOG_FILE="${LOG_DIR}/vllm.log"

# ── Stop service ──
do_stop() {
    if [ -f "$PID_FILE" ]; then
        local PID
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "[vLLM] Stopping service (PID $PID)..."
            kill "$PID" 2>/dev/null || true
            for i in $(seq 1 30); do
                kill -0 "$PID" 2>/dev/null || break
                sleep 1
            done
            if kill -0 "$PID" 2>/dev/null; then
                echo "[vLLM] Force killing..."
                kill -9 "$PID" 2>/dev/null || true
            fi
            echo "[vLLM] Stopped"
        else
            echo "[vLLM] Process $PID not running, cleaning up"
        fi
        rm -f "$PID_FILE"
    else
        echo "[vLLM] No PID file found, service not running"
    fi
    exit 0
}

# ── Arg parsing ──
STOP_MODE=false
while [ $# -gt 0 ]; do
    case "$1" in
        --model)            MODEL_PATH="$2"; shift 2 ;;
        --port)             PORT="$2"; shift 2 ;;
        --gpu-mem-util)     GPU_MEM_UTIL="$2"; shift 2 ;;
        --enable-ep)        ENABLE_EP=true; shift ;;
        --no-ep)            ENABLE_EP=false; shift ;;
        --no-reasoning)     REASONING_PARSER=""; shift ;;
        --gdn-prefill-backend) GDN_PREFILL_BACKEND="$2"; shift 2 ;;
        --moe-backend)        MOE_BACKEND="$2"; shift 2 ;;
        --enforce-eager)      ENFORCE_EAGER=true; shift ;;
        --no-enforce-eager)   ENFORCE_EAGER=false; shift ;;
        --stop)             STOP_MODE=true; shift ;;
        --help|-h)
            echo "Usage: bash $0 [OPTIONS]"
            echo ""
            echo "  --model PATH        Model path (default: /path/to/juicer-checkpoint)"
            echo "  --port N            Port number (default: 8000)"
            echo "  --gpu-mem-util F    GPU memory utilization (default: 0.90)"
            echo "  --enable-ep         Enable Expert Parallel (off by default)"
            echo "  --no-ep             Disable Expert Parallel (default)"
            echo "  --no-reasoning      Disable Reasoning parser"
            echo "  --gdn-prefill-backend NAME  GDN prefill backend (default: vLLM auto)"
            echo "  --moe-backend NAME  MoE kernel backend (default: vLLM auto)"
            echo "  --enforce-eager     Disable torch.compile and CUDA Graphs"
            echo "  --no-enforce-eager  Keep compiled/CUDA Graph mode (default)"
            echo "  --stop              Stop the running service"
            echo "  --help              Show this help"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ── Stop mode ──
if [ "$STOP_MODE" = true ]; then
    do_stop
fi

# ── Startup check ──
if [ ! -d "$MODEL_PATH" ]; then
    echo "[ERROR] Model path does not exist: $MODEL_PATH"
    exit 1
fi

# Check if a service is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[vLLM] Service already running (PID $OLD_PID)"
        echo "  Stop: bash $0 --stop"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

# Device check
GPU_COUNT=$(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | wc -l)
if [ "$GPU_COUNT" -lt 1 ]; then
    echo "[ERROR] No NVIDIA GPU is visible"
    exit 1
fi
if [[ -n "$GDN_PREFILL_BACKEND" && "$GDN_PREFILL_BACKEND" != "triton" && "$GDN_PREFILL_BACKEND" != "flashinfer" && "$GDN_PREFILL_BACKEND" != "cutedsl" ]]; then
    echo "[ERROR] Invalid GDN prefill backend: $GDN_PREFILL_BACKEND" >&2
    exit 1
fi

mkdir -p "$LOG_DIR"

# ── Model name (fixed to juicer, aligned with app.py / examples defaults) ──
MODEL_NAME="juicer"

# ── Build command ──
CMD=(
    python -m vllm.entrypoints.openai.api_server
    --model "$MODEL_PATH"
    --served-model-name "$MODEL_NAME"
    --host 0.0.0.0
    --port "$PORT"
    --gpu-memory-utilization "$GPU_MEM_UTIL"
    --max-model-len "$MAX_MODEL_LEN"
    --max-num-batched-tokens "$MAX_NUM_BATCHED_TOKENS"
    --max-num-seqs "$MAX_NUM_SEQS"
    --trust-remote-code
    --dtype auto
    --language-model-only
)

if [ -n "$GDN_PREFILL_BACKEND" ]; then
    CMD+=(--gdn-prefill-backend "$GDN_PREFILL_BACKEND")
fi

if [ -n "$MOE_BACKEND" ]; then
    CMD+=(--moe-backend "$MOE_BACKEND")
fi

if [ "$ENABLE_EP" = true ]; then
    CMD+=(--enable-expert-parallel)
fi

if [ -n "$REASONING_PARSER" ]; then
    CMD+=(--reasoning-parser "$REASONING_PARSER")
fi

if [ "$ENFORCE_EAGER" = true ]; then
    CMD+=(--enforce-eager)
fi

echo ""
echo "============================================================"
echo "  Juicer vLLM Service"
echo "============================================================"
echo "  Model:       $MODEL_PATH"
echo "  Served as:   $MODEL_NAME"
echo "  EP:          $ENABLE_EP"
echo "  Reasoning:   ${REASONING_PARSER:-disabled}"
echo "  Port:        $PORT"
echo "  GPU mem:     $GPU_MEM_UTIL"
echo "  Max len:     $MAX_MODEL_LEN"
echo "  GDN prefill: ${GDN_PREFILL_BACKEND:-vLLM auto}"
echo "  MoE backend: ${MOE_BACKEND:-vLLM auto}"
echo "  Eager:       $ENFORCE_EAGER"
echo "  GPUs:        $GPU_COUNT"
echo "  Log:         $LOG_FILE"
echo "============================================================"
echo ""

# ── Background start ──
export VLLM_ENGINE_READY_TIMEOUT_S=18000

nohup "${CMD[@]}" > "$LOG_FILE" 2>&1 &
VLLM_PID=$!
echo "$VLLM_PID" > "$PID_FILE"
echo "[vLLM] Started (PID $VLLM_PID), waiting for ready..."

# ── Wait for health check ──
TIMEOUT=18000
START_TIME=$(date +%s)
while true; do
    ELAPSED=$(( $(date +%s) - START_TIME ))
    if [ "$ELAPSED" -gt "$TIMEOUT" ]; then
        echo "[ERROR] vLLM startup timeout (${TIMEOUT}s)"
        echo "  Log: tail -f $LOG_FILE"
        exit 1
    fi

    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
        echo "[ERROR] vLLM process exited unexpectedly"
        echo "  Log: tail -f $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi

    if curl -sf "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        echo ""
        echo "[vLLM] Ready on http://localhost:${PORT} (${ELAPSED}s)"
        echo "[vLLM] API:  http://localhost:${PORT}/v1"
        echo "[vLLM] PID:  $VLLM_PID"
        echo ""
        echo "Test request:"
        echo "  curl http://localhost:${PORT}/v1/chat/completions \\"
        echo "    -H 'Content-Type: application/json' \\"
        echo "    -d '{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}'"
        echo ""
        echo "Stop service:"
        echo "  bash $0 --stop"
        exit 0
    fi

    sleep 5
done
