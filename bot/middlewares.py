from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from db import get_user_from_db


class AccessCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:        
        if not isinstance(event, Message):
            return await handler(event, data)
        user_id = event.from_user.id
        user_data = await get_user_from_db(user_id)        
        if not user_data:
            if event.text == "/start" or event.contact:
                return await handler(event, data)
            return        
        elif user_data["role"] == "block":
            return        
        elif user_data["role"] == "guest":
            if event.text == "/start" or event.contact:
                await event.answer("⏳ Your request is under consideration...")
            return
        else:
            data["user_data"] = user_data
            return await handler(event, data)
