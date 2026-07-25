#!/bin/bash
# CreditMind Demo 自动录屏脚本
# 用法:
#   bash demo/record_demo.sh          # 默认录 120 秒（2 分钟）
#   bash demo/record_demo.sh 90       # 自定义时长（秒）
#
# 后端优先级:
#   1. ffmpeg（含 imageio-ffmpeg 静态二进制）→ avfoundation 录屏 + 麦克风（带声音，输出 MP4）
#   2. 否则 → macOS 自带 screencapture 录屏（无声，零依赖，输出 MOV）
#
# 录制前请先确保 Streamlit Demo 已在运行: streamlit run app.py (http://localhost:8501)
# 注意：运行本脚本的 app（CodeBuddy / Terminal）需在「系统设置→隐私与安全性→屏幕录制」中已授权。

cd "$(dirname "$0")/.."
DUR=${1:-120}
OUT="demo/CreditMind-Demo.mp4"
mkdir -p demo

# 探测 ffmpeg：优先 PATH，其次 imageio-ffmpeg 静态二进制
FF=""
if command -v ffmpeg >/dev/null 2>&1; then
  FF="$(command -v ffmpeg)"
elif /Users/yolanda/anaconda3/bin/python3 -c "import imageio_ffmpeg" >/dev/null 2>&1; then
  FF="$(/Users/yolanda/anaconda3/bin/python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")"
fi

if [ -n "$FF" ]; then
  echo "== 使用 ffmpeg（录屏 + 麦克风，输出 MP4）=="
  echo "ffmpeg: $FF"
  echo "设备: 屏幕 [1] Capture screen 0 + 麦克风 [0] MacBook Pro麦克风"
  echo "将录制 $DUR 秒（带麦克风解说）。请在此期间操作 http://localhost:8501 的 Demo..."
  "$FF" -f avfoundation -framerate 30 -i "1:0" -t "$DUR" \
        -pix_fmt yuv420p -c:v libx264 -preset ultrafast -c:a aac "$OUT"
  echo "== 录制完成（带声音 MP4）: $OUT =="
  ls -lh "$OUT"
else
  echo "== ffmpeg 未就绪，使用 macOS 自带 screencapture（无声，输出 MOV）=="
  OUT_MOV="demo/CreditMind-Demo.mov"
  echo "将录制 $DUR 秒，请在此期间操作 http://localhost:8501 的 Demo..."
  screencapture -v "$OUT_MOV" &
  REC=$!
  sleep "$DUR"
  kill -INT "$REC" 2>/dev/null || true
  wait "$REC" 2>/dev/null || true
  echo "== 录制完成（无声 MOV）: $OUT_MOV =="
  ls -lh "$OUT_MOV"
fi
