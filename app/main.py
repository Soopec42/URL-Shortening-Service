import uvicorn

from app.core.config import get_setting

if __name__ == "__main__":
    setting = get_setting()
    uvicorn.run(
        "app.main:app",
        host=setting.app_host,
        port=setting.app_port
    )



