from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import subprocess
import socket
import datetime
import sys
import os

# Add chatbot module to path
sys.path.append('/home/nhotin/notify_ip')
from chatbot_handler import process_message_external

BOT_TOKEN = '8421359022:AAEOuOW-vL1E-dueOijBsVVK2G3l7Zue0M4'
ALLOWED_CHAT_ID = 2011821810

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    welcome_message = """
🤖 **Server Bot - Integrated System & AI**

📋 **System Commands:**
/ip - Kiểm tra IP
/reboot - Khởi động lại hệ thống
/shutdown - Tắt máy
/status - Trạng thái hệ thống
/uptime - Thời gian hoạt động
/ram - Thông tin RAM
/disk - Thông tin ổ đĩa
/services - Dịch vụ đang chạy
/tailscale - Trạng thái Tailscale
/gpu - Thông tin GPU
/help - Hiển thị trợ giúp
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get server IP address"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get public IP
        try:
            import requests
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "Unable to get public IP"
        
        message = f"🌐 **IP Information**\n\n🏠 Local IP: `{local_ip}`\n🌍 Public IP: `{public_ip}`"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting IP: {str(e)}")

async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reboot system"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    await update.message.reply_text("Rebooting system... Please wait.")
    subprocess.run(["sudo", "reboot"], check=False)

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shutdown system"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    await update.message.reply_text("🔌 Shutting down the system... Goodbye, Boss! 👋")
    subprocess.run(["sudo", "shutdown", "now"], check=False)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system status"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        # CPU usage
        cpu_result = subprocess.run(["top", "-bn1"], capture_output=True, text=True)
        cpu_line = [line for line in cpu_result.stdout.split('\n') if 'Cpu(s)' in line]
        cpu_info = cpu_line[0] if cpu_line else "CPU info not available"
        
        # Memory usage
        mem_result = subprocess.run(["free", "-h"], capture_output=True, text=True)
        mem_lines = mem_result.stdout.strip().split('\n')
        
        # Load average
        load_result = subprocess.run(["uptime"], capture_output=True, text=True)
        load_info = load_result.stdout.strip()
        
        message = f"""📊 **System Status**

💻 **CPU:** {cpu_info.split(':')[1].strip() if ':' in cpu_info else cpu_info}

🧠 **Memory:**
```
{mem_lines[1] if len(mem_lines) > 1 else 'Memory info not available'}
```

⚡ **Load:** {load_info.split('load average:')[1].strip() if 'load average:' in load_info else load_info}
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting status: {str(e)}")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get system uptime"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        uptime_info = result.stdout.strip()
        await update.message.reply_text(f"⏰ **System Uptime:** {uptime_info}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting uptime: {str(e)}")

async def ram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get RAM information"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        result = subprocess.run(["free", "-h"], capture_output=True, text=True)
        ram_info = result.stdout
        message = f"🧠 **RAM Information:**\n```\n{ram_info}\n```"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting RAM info: {str(e)}")

async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get disk information"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        result = subprocess.run(["df", "-h"], capture_output=True, text=True)
        disk_info = result.stdout
        message = f"💾 **Disk Information:**\n```\n{disk_info}\n```"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting disk info: {str(e)}")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get running services"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        result = subprocess.run(["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"], capture_output=True, text=True)
        services_info = result.stdout
        # Limit output to avoid message too long
        lines = services_info.split('\n')[:20]
        limited_info = '\n'.join(lines)
        message = f"🔧 **Running Services (Top 20):**\n```\n{limited_info}\n```"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting services: {str(e)}")

async def tailscale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Tailscale status"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        result = subprocess.run(["tailscale", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            tailscale_info = result.stdout
            message = f"🔗 **Tailscale Status:**\n```\n{tailscale_info}\n```"
        else:
            message = "❌ Tailscale not available or not running"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting Tailscale status: {str(e)}")

async def gpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get GPU information"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    try:
        # Try nvidia-smi first
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info = result.stdout
            message = f"🎮 **GPU Information:**\n```\n{gpu_info}\n```"
        else:
            # Fallback to lspci
            result = subprocess.run(["lspci", "|grep", "-i", "vga"], capture_output=True, text=True, shell=True)
            gpu_info = result.stdout if result.stdout else "No GPU information available"
            message = f"🎮 **GPU Information:**\n```\n{gpu_info}\n```"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting GPU info: {str(e)}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    help_text = """
🤖 **Server Bot - Help**

📋 **Available Commands:**

🌐 `/ip` - Hiển thị địa chỉ IP local và public
🔄 `/reboot` - Khởi động lại hệ thống
🔌 `/shutdown` - Tắt máy
📊 `/status` - Hiển thị trạng thái hệ thống (CPU, RAM, Load)
⏰ `/uptime` - Thời gian hoạt động của hệ thống
🧠 `/ram` - Thông tin chi tiết về RAM
💾 `/disk` - Thông tin về ổ đĩa
🔧 `/services` - Danh sách dịch vụ đang chạy
🔗 `/tailscale` - Trạng thái Tailscale VPN
🎮 `/gpu` - Thông tin GPU
❓ `/help` - Hiển thị trợ giúp này

💡 **Lưu ý:** Bot này chỉ xử lý các lệnh hệ thống. Để chat AI, hãy sử dụng FRYDAY bot!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages with Ollama Chatbot"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    
    user_message = update.message.text.strip()
    
    try:
        # Process message with Ollama Chatbot
        response = process_message_external(user_message)
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý tin nhắn: {str(e)}")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("❓ Unknown command, type /help to see available commands!")

# Bot setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ip", ip))
app.add_handler(CommandHandler("reboot", reboot))
app.add_handler(CommandHandler("shutdown", shutdown))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("uptime", uptime))
app.add_handler(CommandHandler("ram", ram))
app.add_handler(CommandHandler("disk", disk))
app.add_handler(CommandHandler("services", services))
app.add_handler(CommandHandler("tailscale", tailscale))
app.add_handler(CommandHandler("gpu", gpu))
app.add_handler(CommandHandler("help", help_cmd))

# Handle regular text messages with FRYDAY AI
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

# Handle unknown commands
app.add_handler(MessageHandler(filters.COMMAND, unknown))

print("🤖 Server Bot đang chạy - Tích hợp System Commands & FRYDAY AI...")
app.run_polling()
