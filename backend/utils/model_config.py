"""
Model configuration for different AI providers
"""
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class ModelConfig:
    """Configuration for different AI models"""
    
    AVAILABLE_MODELS = {
        # Gemini Models
        "gemini-2.5-flash": {
            "provider": "gemini",
            "name": "Gemini 2.5 Flash",
            "description": "Fast, efficient (Free: 5 RPM, 20 RPD)",
            "api_key_env": "GEMINI_API_KEY",
            "limits": "5 RPM / 20 RPD"
        },
        "gemini-2.5-pro": {
            "provider": "gemini",
            "name": "Gemini 2.5 Pro",
            "description": "More capable, slower (Free: 2 RPM, 10 RPD)",
            "api_key_env": "GEMINI_API_KEY",
            "limits": "2 RPM / 10 RPD"
        },
        "gemini-2.0-flash": {
            "provider": "gemini",
            "name": "Gemini 2.0 Flash",
            "description": "Previous generation, stable",
            "api_key_env": "GEMINI_API_KEY",
            "limits": "5 RPM / 20 RPD"
        },
        "gemini-2.5-flash-lite": {
            "provider": "gemini",
            "name": "Gemini 2.5 Flash Lite",
            "description": "Ultra-fast, basic tasks",
            "api_key_env": "GEMINI_API_KEY",
            "limits": "10 RPM / 40 RPD"
        },
    }
    
    @classmethod
    def get_model_info(cls, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        return cls.AVAILABLE_MODELS.get(model_id, cls.AVAILABLE_MODELS["gemini-2.5-flash"])
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """Get dict of model_id: display_name for dropdown"""
        return {
            model_id: f"{info['name']} - {info['limits']}"
            for model_id, info in cls.AVAILABLE_MODELS.items()
        }
    
    @classmethod
    def is_model_available(cls, model_id: str) -> bool:
        """Check if model can be used (API key exists)"""
        if model_id not in cls.AVAILABLE_MODELS:
            return False
        
        model_info = cls.AVAILABLE_MODELS[model_id]
        api_key_env = model_info.get("api_key_env")
        
        if not api_key_env:
            return True
        
        return bool(os.getenv(api_key_env))
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default model ID"""
        return "gemini-2.5-flash"
