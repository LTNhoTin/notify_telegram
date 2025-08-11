# Server Bot với AI (Ollama GPT-OSS:20B)

Hệ thống thông báo, lệnh hệ thống và chatbot AI tích hợp sử dụng **Telegram Bot** & **Ollama**.

## 🚀 Cài đặt & Sử dụng

### 1. Chạy script tích hợp
```bash
./notify_ip.sh
```
Script này sẽ:
- Gửi thông báo IP qua Telegram
- Khởi động Ollama server
- Tải model AI (nếu chưa có)
- Khởi động Telegram Bot với AI

### 2. Cài đặt thủ công (nếu cần)

#### Cài dependencies
```bash
# Tạo môi trường ảo
python3 -m venv botenv
source botenv/bin/activate
pip install requests python-telegram-bot
```

#### Cài Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Tải model AI
```bash
ollama pull gpt-oss:20b
```

## 📱 Lệnh Telegram Bot

### 🔧 System Commands
- `/start` — Khởi động bot & hiển thị menu
- `/ip` — Xem IP (local + public)
- `/status` — Trạng thái hệ thống (CPU, RAM)
- `/uptime` — Thời gian hoạt động
- `/ram` — Chi tiết RAM
- `/disk` — Thông tin ổ đĩa
- `/gpu` — Thông tin GPU
- `/services` — Dịch vụ đang chạy
- `/tailscale` — Trạng thái Tailscale
- `/reboot` — Khởi động lại hệ thống
- `/shutdown` — Tắt máy
- `/help` — Trợ giúp

### 🤖 AI Chat
Gửi tin nhắn (không bắt đầu bằng `/`) để chat với AI:
- `Xin chào, bạn có thể giúp tôi không?`
- `Giải thích về machine learning`
- `Viết code Python để đọc file CSV`

## 🔧 Cấu hình

### Bot Token & Chat ID
Trong `server_bot.py`:
```python
BOT_TOKEN = 'YOUR_BOT_TOKEN'
ALLOWED_CHAT_ID = YOUR_CHAT_ID
```

### Ollama Model
Trong `chatbot_handler.py`:
```python
class OllamaChatbot:
    def __init__(self, base_url="http://localhost:11434", model="gpt-oss:20b"):
```

### Ollama Server URL (chạy trên server khác)
```python
chatbot = OllamaChatbot(base_url="http://your-server:11434")
```

## 📁 Cấu trúc dự án
```
notify_ip/
├── notify_ip.sh           # Script tích hợp: thông báo IP + khởi động AI bot
├── server_bot.py          # Telegram bot chính
├── chatbot_handler.py     # Xử lý AI chatbot với Ollama
├── README.md              # Hướng dẫn này
├── GETTING_STARTED.md     # Hướng dẫn nhanh
└── botenv/                # Python virtual environment
```

> **Lưu ý**: Model `gpt-oss:20b` cần **>10GB RAM và storage**.
