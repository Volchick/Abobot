from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.config_reader import VK_CLIENT_ID, VK_CLIENT_SECRET, VK_REDIRECT_URI
from app.database import get_async_session
from app.models import User
import httpx
from fastapi.responses import HTMLResponse

app = FastAPI()

# Обрабатывает callback от VK OAuth.
@app.get("/vk/callback")
async def vk_callback(
    request: Request,
    code: str,
    state: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id = int(state)
        token_url = "https://oauth.vk.com/access_token"
        params = {
            "client_id": VK_CLIENT_ID,
            "client_secret": VK_CLIENT_SECRET,
            "redirect_uri": VK_REDIRECT_URI,
            "code": code
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(token_url, params=params)
            response.raise_for_status()
            token_data = response.json()

            user = await session.get(User, user_id)
            if not user:
                user = User(telegram_id=user_id, username=None)
                session.add(user)

            user.vk_access_token = token_data.get("access_token")
            user.vk_refresh_token = token_data.get("refresh_token")
            user.vk_user_id = token_data.get("user_id")

            await session.commit()
            return HTMLResponse("<h2>Авторизация прошла успешно! Вы можете закрыть это окно.</h2>")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))