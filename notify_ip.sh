#!/bin/bash

BOT_TOKEN="8421359022:AAEOuOW-vL1E-dueOijBsVVK2G3l7Zue0M4"
CHAT_ID="2011821810"

escape_md() {
  # Escape các ký tự markdown nguy hiểm nhất: ` * _ [
  echo "$1" | sed -e 's/`/\\`/g' -e 's/*/\\*/g' -e 's/_/\\_/g' -e 's/\[/\\[/g' -e 's/\]/\\]/g'
}

# ===== Basic Info =====
IP=$(curl -s https://api.ipify.org || echo "Unknown")
HOSTNAME=$(hostname)
NODE_ID=$(echo $HOSTNAME | md5sum | cut -c1-8)
OS=$(lsb_release -d 2>/dev/null | awk -F'\t' '{print $2}' || echo "$(uname -s) $(uname -r)")
UPTIME=$(uptime -p)
LAN_IP=$(hostname -I | awk '{print $1}' || echo "N/A")
TIME=$(date "+%Y-%m-%d %H:%M:%S")

# ===== CPU/RAM Info =====
CPU_INFO=$(lscpu | grep "Model name" | awk -F': ' '{print $2}' | sed 's/^[ \t]*//')
CPU_CORES=$(nproc)
LOAD_1=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
LOAD_5=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f2 | xargs)
LOAD_15=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f3 | xargs)

MEMORY_TOTAL=$(free -h | awk 'NR==2{print $2}')
MEMORY_USED=$(free -h | awk 'NR==2{print $3}')
MEMORY_FREE=$(free -h | awk 'NR==2{print $4}')
MEMORY_PERCENT=$(free | awk 'NR==2{printf "%.0f%%", $3*100/$2}')

# ===== RAM Brand/Model =====
RAM_INFO=""
if command -v dmidecode >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
    RAM_BRAND=$(dmidecode -t memory | grep -i "manufacturer" | head -1 | awk -F': ' '{print $2}' | xargs)
    RAM_MODEL=$(dmidecode -t memory | grep -i "part number" | head -1 | awk -F': ' '{print $2}' | xargs)
    RAM_SPEED=$(dmidecode -t memory | grep -i "speed" | head -1 | awk -F': ' '{print $2}' | xargs)
    if [ -n "$RAM_BRAND" ] && [ -n "$RAM_MODEL" ]; then
        RAM_INFO="$RAM_BRAND $RAM_MODEL @$RAM_SPEED"
    fi
fi

# ===== GPU Info =====
GPU_INFO="Not detected"
if command -v lspci >/dev/null 2>&1; then
    GPU_LIST=$(lspci | grep -i vga | awk -F': ' '{print $2}')
    [ -n "$GPU_LIST" ] && GPU_INFO="$GPU_LIST"
    if command -v nvidia-smi >/dev/null 2>&1; then
        NVIDIA_INFO=$(nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
        if [ -n "$NVIDIA_INFO" ]; then
            GPU_NAME=$(echo "$NVIDIA_INFO" | cut -d',' -f1)
            GPU_TEMP=$(echo "$NVIDIA_INFO" | cut -d',' -f2)
            GPU_UTIL=$(echo "$NVIDIA_INFO" | cut -d',' -f3)
            GPU_MEM_USED=$(echo "$NVIDIA_INFO" | cut -d',' -f4)
            GPU_MEM_TOTAL=$(echo "$NVIDIA_INFO" | cut -d',' -f5)
            GPU_INFO="$GPU_NAME (${GPU_TEMP}°C, ${GPU_UTIL}% load, ${GPU_MEM_USED}MB/${GPU_MEM_TOTAL}MB)"
        fi
    fi
fi

# ===== Disk Info (All Disks) =====
DISK_LIST=$(df -h -x tmpfs -x devtmpfs --output=source,size,used,pcent,target | grep '^/dev/' | grep -v '/boot\|/snap')
DISK_INFO=""
DISK_COUNT=0
while read -r line; do
    DEV=$(echo $line | awk '{print $1}')
    SIZE=$(echo $line | awk '{print $2}')
    USED=$(echo $line | awk '{print $3}')
    PCENT=$(echo $line | awk '{print $4}')
    MNT=$(echo $line | awk '{print $5}')
    DISK_INFO="$DISK_INFO
   └─ \`$DEV\` (\`$MNT\`): $USED/$SIZE ($PCENT)"
    DISK_COUNT=$((DISK_COUNT + 1))
done <<< "$DISK_LIST"

# ===== Tailscale Network Info =====
TAILSCALE_STATUS="🔴 Offline"
TAILSCALE_IP=""
if command -v tailscale >/dev/null 2>&1; then
    if tailscale status >/dev/null 2>&1; then
        TAILSCALE_STATUS="🟢 Online"
        TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "")
    else
        TAILSCALE_STATUS="🟡 Installed, not connected"
    fi
fi

# ===== Service Checkers =====
check_service() {
    if systemctl is-active --quiet "$1"; then echo "🟢 Online"; else echo "🔴 Offline"; fi
}
get_status_icon() {
    if systemctl is-active --quiet "$1"; then echo "🟢"; else echo "🔴"; fi
}
# SSH
SSH_STATUS=$(check_service ssh)
SSH_ICON=$(get_status_icon ssh)
# Docker
DOCKER_STATUS=$(check_service docker)
DOCKER_ICON=$(get_status_icon docker)
# Nginx
NGINX_STATUS=$(check_service nginx)
NGINX_ICON=$(get_status_icon nginx)
# Nextcloud (docker, port 8888)
NEXTCLOUD_ICON="🔴"
NEXTCLOUD_STATUS="🔴 Offline"
if command -v docker >/dev/null 2>&1; then
    if docker ps --format '{{.Names}} {{.Ports}}' | grep -E 'nextcloud.*0.0.0.0:8888->80/tcp' >/dev/null; then
        NEXTCLOUD_ICON="🟢"
        NEXTCLOUD_STATUS="🟢 Online"
    fi
fi

# ===== Internet Check =====
INTERNET_STATUS="🟢 Online"
if ! curl -s --connect-timeout 5 https://google.com >/dev/null; then
    INTERNET_STATUS="🔴 Offline"
fi

# ===== CPU Temp =====
TEMP="N/A"
if command -v vcgencmd >/dev/null 2>&1; then
    TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 || echo "N/A")
elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP_RAW=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMP="$((TEMP_RAW/1000))°C"
fi

# ===== AI Greetings =====
AI_GREETINGS=(
    "🤖 NEXUS AI ONLINE — Hi, Boss!"
    "🧠 SYSTEM AWAKENED — Neural networks initialized!"
    "⚡ QUANTUM READY — All systems optimal!"
    "🚀 MISSION CONTROL — Ready for launch!"
    "💎 PRIME DIRECTIVE — Efficiency max!"
    "🔮 ORACLE MODE — Server companion online!"
    "🎯 TACTICAL AI — Strategic ops ready!"
    "🌟 SINGULARITY — Booting excellence!"
)
RANDOM_GREETING=${AI_GREETINGS[$RANDOM % ${#AI_GREETINGS[@]}]}

# ===== Build Telegram Message =====
MESSAGE="

$RANDOM_GREETING

━━━━━━━━━━━━━━━
🖥️ Host: $HOSTNAME
🌐 Node ID: \`$NODE_ID\`
━━━━━━━━━━━━━━━

Network
━━━━━━━━━━━━━━━
$INTERNET_STATUS Internet
🌍 Public IP: $IP
🏠 Local IP: $LAN_IP
🔐 Tailscale: $TAILSCALE_STATUS"
if [ -n "$TAILSCALE_IP" ]; then
    MESSAGE="$MESSAGE
   └─ VPN IP: \`$TAILSCALE_IP\`"
fi

MESSAGE="$MESSAGE

System
━━━━━━━━━━━━━━━
🖥️ OS: $OS
⚡ CPU: \`$CPU_INFO\` ($CPU_CORES cores)
📊 Load: $LOAD_1 | $LOAD_5 | $LOAD_15 (1m|5m|15m)"
[ -n "$RAM_INFO" ] && MESSAGE="$MESSAGE
🎯 RAM: \`$RAM_INFO\`"
MESSAGE="$MESSAGE
🧠 Memory: $MEMORY_USED/$MEMORY_TOTAL ($MEMORY_PERCENT used)
   └─ Free: $MEMORY_FREE
🎮 GPU: \`$GPU_INFO\`
💾 Disks: $DISK_COUNT disk(s)$DISK_INFO"
[ "$TEMP" != "N/A" ] && MESSAGE="$MESSAGE
🌡️ CPU Temp: $TEMP"
MESSAGE="$MESSAGE
⏱️ Uptime: $UPTIME
📅 Time: $TIME

Services
━━━━━━━━━━━━━━━
$SSH_ICON SSH  |  $DOCKER_ICON Docker  
$NGINX_ICON Nginx  |  $NEXTCLOUD_ICON Nextcloud

━━━━━━━━━━━━━━━
🎯 AI STATUS: FULLY OPERATIONAL 🎯

I'm ready, Boss! 🚀✨
"

# ===== Send Telegram Message =====
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d text="${MESSAGE}" \
  -d parse_mode="Markdown"

# ===== Start Ollama and Server Bot =====
echo "🤖 Starting Ollama and Server Bot..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed. Please run: sudo ./setup_autostart.sh"
    exit 1
fi

# Start Ollama server in background
echo "🔄 Starting Ollama server..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
echo "Ollama PID: $OLLAMA_PID"

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama server is running"
else
    echo "❌ Ollama server failed to start"
    kill $OLLAMA_PID 2>/dev/null
    exit 1
fi

# Check if model exists
echo "🔍 Checking for gpt-oss:20b model..."
if ollama list | grep -q "gpt-oss:20b"; then
    echo "✅ Model gpt-oss:20b is available"
else
    echo "📥 Model gpt-oss:20b not found, pulling..."
    echo "⚠️ This may take a long time (model >10GB)"
    ollama pull gpt-oss:20b
    if [ $? -eq 0 ]; then
        echo "✅ Model downloaded successfully"
    else
        echo "❌ Failed to download model"
        echo "💡 You can download it later: ollama pull gpt-oss:20b"
    fi
fi

# Start Server Bot
echo "🤖 Starting Server Bot..."
echo "✅ Bot will run in background"
echo "✅ To stop: pkill -f server_bot.py"
echo "✅ To view logs: tail -f /tmp/server_bot.log"

# Activate virtual environment and start bot
source botenv/bin/activate
nohup python server_bot.py > /tmp/server_bot.log 2>&1 &
BOT_PID=$!
echo "Server Bot PID: $BOT_PID"
deactivate

# Wait a moment to check if bot started successfully
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Server Bot started successfully"
    echo "🎉 System is fully operational!"
    echo ""
    echo "📋 Process IDs:"
    echo "   Ollama: $OLLAMA_PID"
    echo "   Server Bot: $BOT_PID"
    echo ""
    echo "📝 Useful commands:"
    echo "   Stop Ollama: kill $OLLAMA_PID"
    echo "   Stop Bot: kill $BOT_PID"
    echo "   View Bot logs: tail -f /tmp/server_bot.log"
else
    echo "❌ Server Bot failed to start"
    echo "📝 Check logs: cat /tmp/server_bot.log"
    kill $OLLAMA_PID 2>/dev/null
    exit 1
fi
