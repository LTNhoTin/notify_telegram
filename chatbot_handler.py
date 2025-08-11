import requests
import json
import logging
from typing import Optional

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaChatbot:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        """
        Khởi tạo chatbot với Ollama server
        
        Args:
            base_url: URL của Ollama server (mặc định: http://localhost:11434)
            model: Tên model sử dụng (mặc định: gpt-oss:20b)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_url = f"{self.base_url}/api/generate"
        
    def is_server_available(self) -> bool:
        """
        Kiểm tra xem Ollama server có hoạt động không
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Không thể kết nối đến Ollama server: {e}")
            return False
    
    def check_model_exists(self) -> bool:
        """
        Kiểm tra xem model có tồn tại trên server không
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                return any(self.model in name for name in model_names)
            return False
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra model: {e}")
            return False
    
    def generate_response(self, message: str, system_prompt: str = None) -> Optional[str]:
        """
        Tạo phản hồi từ chatbot
        
        Args:
            message: Tin nhắn từ người dùng
            system_prompt: Prompt hệ thống (tùy chọn)
            
        Returns:
            Phản hồi từ chatbot hoặc None nếu có lỗi
        """
        try:
            # Kiểm tra server và model
            if not self.is_server_available():
                return "❌ Ollama server không hoạt động. Vui lòng kiểm tra lại."
            
            if not self.check_model_exists():
                return f"❌ Model '{self.model}' không tồn tại trên server. Vui lòng kiểm tra lại."
            
            # Chuẩn bị prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {message}\n\nAssistant:"
            else:
                full_prompt = f"User: {message}\n\nAssistant:"
            
            # Chuẩn bị payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            # Gửi request
            logger.info(f"Gửi request đến Ollama với model: {self.model}")
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Lỗi API: {response.status_code} - {response.text}")
                return f"❌ Lỗi từ server: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Timeout khi gọi API")
            return "⏰ Timeout - Server phản hồi quá chậm. Vui lòng thử lại."
        except requests.exceptions.ConnectionError:
            logger.error("Lỗi kết nối đến Ollama server")
            return "❌ Không thể kết nối đến Ollama server. Vui lòng kiểm tra server."
        except Exception as e:
            logger.error(f"Lỗi không mong muốn: {e}")
            return f"❌ Lỗi: {str(e)}"
    
    def get_available_models(self) -> list:
        """
        Lấy danh sách các model có sẵn
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model.get('name', '') for model in models]
            return []
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách model: {e}")
            return []

# Khởi tạo chatbot instance
chatbot = OllamaChatbot()

def process_message_external(message: str) -> str:
    """
    Hàm xử lý tin nhắn từ bên ngoài (để tương thích với server_bot.py)
    
    Args:
        message: Tin nhắn cần xử lý
        
    Returns:
        Phản hồi từ chatbot
    """
    system_prompt = (
        "Bạn là một trợ lý AI thông minh và hữu ích. "
        "Hãy trả lời một cách tự nhiên, thân thiện và chính xác. "
        "Bạn có thể trả lời bằng tiếng Việt hoặc tiếng Anh tùy theo ngôn ngữ của câu hỏi."
    )
    
    response = chatbot.generate_response(message, system_prompt)
    return response or "❌ Không thể tạo phản hồi. Vui lòng thử lại."

if __name__ == "__main__":
    # Test chatbot
    print("🤖 Testing Ollama Chatbot...")
    print(f"Server available: {chatbot.is_server_available()}")
    print(f"Model exists: {chatbot.check_model_exists()}")
    print(f"Available models: {chatbot.get_available_models()}")
    
    # Test message
    test_message = "Xin chào, bạn có thể giúp tôi không?"
    response = process_message_external(test_message)
    print(f"Test response: {response}")