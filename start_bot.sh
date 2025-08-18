#!/bin/bash

# Script để khởi động bot mà không ảnh hưởng đến terminal người dùng
# Chạy trong background và không activate virtual environment cho terminal hiện tại

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Starting Ollama and Server Bot..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed. Please install Ollama first."
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

# Start Server Bot in isolated environment
echo "🤖 Starting Server Bot..."
echo "✅ Bot will run in background"
echo "✅ To stop: pkill -f server_bot.py"
echo "✅ To view logs: tail -f /tmp/server_bot.log"

# Start bot in completely isolated environment
echo "🚀 Starting bot in isolated environment..."
(
    # Ensure we're in the right directory
    cd "$(dirname "$0")"
    
    # Activate virtual environment in subshell
    source botenv/bin/activate
    
    # Start bot with nohup to detach from terminal
    nohup python server_bot.py > /tmp/server_bot.log 2>&1 &
    BOT_PID=$!
    echo "Server Bot PID: $BOT_PID"
    
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
)