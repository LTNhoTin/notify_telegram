# Hướng dẫn sử dụng Notify IP Bot

## Tổng quan
Hệ thống Notify IP Bot đã được cập nhật với các tính năng mới:

### 1. Tính năng DDNS Manual Update
- **Command**: `/ddns`
- **Mô tả**: Cập nhật DDNS thủ công qua Telegram
- **Cách sử dụng**: Gửi `/ddns` trong chat Telegram với bot
- **Lưu ý**: Không ảnh hưởng đến việc tự động cập nhật DDNS mỗi 5 phút

### 2. Sửa lỗi Virtual Environment
- **Vấn đề cũ**: Mỗi lần mở terminal mới đều tự động activate virtual environment
- **Giải pháp**: Tách riêng script khởi động bot (`start_bot.sh`) để không ảnh hưởng đến terminal người dùng
- **Kết quả**: Terminal người dùng giờ đây sạch sẽ, chỉ có conda base environment

## Cấu trúc file

```
/home/nhotin/notify_ip/
├── notify_ip.sh          # Script chính gửi thông báo và khởi động bot
├── start_bot.sh          # Script riêng để khởi động bot (mới)
├── server_bot.py         # Bot Telegram với command /ddns mới
├── chatbot_handler.py    # Xử lý AI chatbot
├── USAGE.md              # File hướng dẫn này
└── botenv/              # Virtual environment (không ảnh hưởng terminal)
```

## DDNS Configuration

### Tự động cập nhật
- **Service**: `ddclient.service`
- **Interval**: 300 giây (5 phút)
- **Status**: Đang chạy tự động
- **Config**: `/etc/ddclient.conf`

### Manual update qua Telegram
- **Command**: `/ddns`
- **Chức năng**: Force update DDNS ngay lập tức
- **Output**: Hiển thị IP hiện tại và kết quả cập nhật

## Các command Telegram khả dụng

```
/start    - Khởi động bot và hiển thị menu
/ip       - Kiểm tra IP local và public
/ddns     - Cập nhật DDNS manual (MỚI)
/status   - Trạng thái hệ thống
/uptime   - Thời gian hoạt động
/ram      - Thông tin RAM
/disk     - Thông tin ổ đĩa
/services - Dịch vụ đang chạy
/tailscale- Trạng thái Tailscale
/gpu      - Thông tin GPU
/reboot   - Khởi động lại hệ thống
/shutdown - Tắt máy
/help     - Hiển thị trợ giúp
```

## 🚀 Khởi động hệ thống

### Tự động (khuyến nghị)
Hệ thống sẽ tự động khởi động khi boot thông qua systemd service:
```bash
sudo systemctl status notify-ip.service
```

### Thủ công
Nếu cần khởi động thủ công:
```bash
cd /home/nhotin/notify_ip
./start_bot.sh
```

## 🛠️ Quản lý hệ thống

### Khởi động lại services
```bash
cd /home/nhotin/notify_ip
# Dừng processes hiện tại
pkill -f "python.*server_bot.py"
pkill -f "ollama serve"
# Khởi động lại
./start_bot.sh
```

## Logs và Monitoring

### Bot logs
```bash
tail -f /tmp/server_bot.log
```

### DDNS logs
```bash
sudo journalctl -u ddclient -f
```

### System service logs
```bash
sudo journalctl -u notify-ip -f
```

## Troubleshooting

### Bot không khởi động
1. Kiểm tra Ollama: `ollama list`
2. Kiểm tra virtual environment: `ls -la /home/nhotin/notify_ip/botenv`
3. Xem logs: `cat /tmp/server_bot.log`

### DDNS không cập nhật
1. Kiểm tra service: `sudo systemctl status ddclient`
2. Test manual: `sudo ddclient -force -verbose`
3. Kiểm tra config: `sudo cat /etc/ddclient.conf`

### Virtual environment issues
- Vấn đề đã được giải quyết bằng cách tách riêng script khởi động
- Terminal người dùng không còn bị ảnh hưởng
- Bot chạy trong môi trường isolated

## Cập nhật gần đây

✅ **Đã hoàn thành**:
1. Thêm command `/ddns` để cập nhật DDNS manual
2. Sửa lỗi virtual environment ảnh hưởng terminal
3. Tách riêng script khởi động bot
4. Cập nhật help messages
5. Xác nhận ddclient service chạy đúng interval 5 phút