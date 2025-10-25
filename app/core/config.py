from pydantic_settings import BaseSettings
from typing import Optional, Union, List
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "CRM API"
    
    # CORS - can be a JSON string or list
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    def model_post_init(self, __context):
        # Convert CORS origins string to list if needed
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                self.BACKEND_CORS_ORIGINS = json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                # If not valid JSON, treat as single origin
                if self.BACKEND_CORS_ORIGINS == "*":
                    self.BACKEND_CORS_ORIGINS = ["*"]
                else:
                    self.BACKEND_CORS_ORIGINS = [self.BACKEND_CORS_ORIGINS]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

