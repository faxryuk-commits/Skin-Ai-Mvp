import logging
from typing import Any, Dict, List

import aiohttp
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout

from config import get_settings
from keyboards import main_actions
from messages import (
    ASK_FOR_PHOTO_RU,
    BAD_QUALITY_RU,
    CONSENT_REMINDER_RU,
    ERROR_RU,
    INTRO_RU,
    PROCESSING_RU,
    REPORT_TEMPLATE_RU,
    SAVE_PROMPT_RU,
)


settings = get_settings()
session = AiohttpSession(timeout=ClientTimeout(total=60, sock_connect=30, sock_read=30))
bot = Bot(
    token=settings.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    await message.answer(f"{INTRO_RU}\n\n{CONSENT_REMINDER_RU}")


def format_bullet_list(items: List[str]) -> str:
    if not items:
        return "• —"
    return "\n".join(f"• {item}" for item in items)


def build_report(payload: Dict[str, Any]) -> str:
    concerns = ", ".join(payload.get("concerns") or []) or "—"
    routine = payload.get("routine") or {}
    morning = format_bullet_list(routine.get("morning") or [])
    evening = format_bullet_list(routine.get("evening") or [])
    ingredients = ", ".join(payload.get("ingredients") or []) or "—"
    product_classes = ", ".join(payload.get("product_classes") or []) or "—"

    return REPORT_TEMPLATE_RU.format(
        age=payload.get("age_band", "—"),
        skin_type=payload.get("skin_type", "—"),
        concerns=concerns,
        morning=morning,
        evening=evening,
        ingredients=ingredients,
        products=product_classes,
    )


async def fetch_photo_bytes(file_id: str) -> bytes:
    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{settings.token}/{file.file_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            response.raise_for_status()
            return await response.read()


async def request_analysis(image_bytes: bytes, user_id: int) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field("file", image_bytes, filename="face.jpg", content_type="image/jpeg")
        form.add_field("user_id", str(user_id))
        async with session.post(f"{settings.api_base_url}/analyze", data=form, timeout=120) as response:
            if response.status == 422:
                raise ValueError("bad_quality")
            response.raise_for_status()
            return await response.json()


@router.message(F.photo)
async def on_photo(message: types.Message) -> None:
    await message.answer(PROCESSING_RU)
    photo = message.photo[-1]
    try:
        image_bytes = await fetch_photo_bytes(photo.file_id)
        payload = await request_analysis(image_bytes, message.from_user.id)
    except ValueError as exc:
        if str(exc) == "bad_quality":
            await message.answer(BAD_QUALITY_RU)
            return
        logger.exception("Ошибка качества изображения: %s", exc)
        await message.answer(ERROR_RU)
        return
    except Exception as exc:  # noqa: BLE001
        logger.exception("Сбой анализа: %s", exc)
        await message.answer(ERROR_RU)
        return

    report_text = build_report(payload)
    await message.answer(report_text, reply_markup=main_actions())
    await message.answer(SAVE_PROMPT_RU)


@router.message()
async def on_non_photo(message: types.Message) -> None:
    await message.answer(ASK_FOR_PHOTO_RU)


@router.callback_query(F.data == "show_terms")
async def show_terms(callback: CallbackQuery) -> None:
    if settings.terms_url or settings.privacy_url:
        parts = []
        if settings.terms_url:
            parts.append(f"• <a href=\"{settings.terms_url}\">Условия использования</a>")
        if settings.privacy_url:
            parts.append(f"• <a href=\"{settings.privacy_url}\">Политика конфиденциальности</a>")
        text = "\n".join(parts)
    else:
        text = settings.privacy_disclaimer
    await callback.message.answer(text)
    await callback.answer()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()

