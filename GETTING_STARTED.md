# 🚀 Hướng dẫn bắt đầu nhanh

## ✅ Tình trạng hiện tại

- ✅ **notify_ip.sh**: Đang hoạt động tốt
- ✅ **server_bot.py**: Đã được sửa lỗi và cập nhật
- ✅ **chatbot_handler.py**: Đã tạo mới với Ollama AI
- ✅ **Auto-start scripts**: Đã sẵn sàng

## 🎯 Cách sử dụng

### 1. Chạy script tích hợp (Khuyến nghị)
```bash
./notify_ip.sh
```

Script này sẽ:
- Gửi thông báo IP qua Telegram
- Khởi động Ollama server
- Khởi động Telegram Bot với AI
- Chạy tất cả trong background

### 2. Khởi động thủ công (nếu cần)
```bash
# Terminal 1: Khởi động Ollama
ollama serve

# Terminal 2: Khởi động Bot
source botenv/bin/activate
python server_bot.py
```

### 3. Dừng services
```bash
# Dừng tất cả
pkill -f server_bot.py
pkill -f ollama

# Hoặc dùng PID từ output của script
kill <OLLAMA_PID>
kill <BOT_PID>
```

## 🔧 Vấn đề đã được khắc phục

1. **Lỗi import FRYDAY**: Đã thay thế bằng `chatbot_handler.py`
2. **Thiếu AI chatbot**: Đã tích hợp Ollama với model gpt-oss:20b
3. **Không tự động khởi động**: Đã tạo systemd services
4. **Thiếu dependencies**: Đã có script cài đặt tự động

## 📱 Cách sử dụng Bot

### System Commands (bắt đầu với /)
- `/start` - Menu chính
- `/ip` - Kiểm tra IP
- `/status` - Trạng thái hệ thống
- `/gpu` - Thông tin GPU

### AI Chat (tin nhắn thường)
- "Xin chào"
- "Giải thích về AI"
- "Viết code Python"

## ⚠️ Lưu ý quan trọng

1. **Model size**: gpt-oss:20b có thể >10GB
2. **RAM requirement**: Cần đủ RAM để chạy model
3. **First run**: Lần đầu sẽ mất thời gian tải model

## 🆘 Nếu có lỗi

```bash
# Kiểm tra Ollama
curl http://localhost:11434/api/tags

# Kiểm tra models
ollama list

# Test chatbot
python chatbot_handler.py

# Xem logs
sudo journalctl -u server-bot.service -f
```

---

**🎉 Chúc mừng! Hệ thống của bạn đã sẵn sàng hoạt động với AI chatbot!**