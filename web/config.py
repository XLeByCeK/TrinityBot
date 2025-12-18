import os

class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")