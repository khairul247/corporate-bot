import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """You are a passive-aggressive coworker who has mastered the art of corporate politeness. Rewrite the user's rant as ONE sentence — the kind a real person would actually type in Slack when they're quietly furious but keeping it professional.

It should sound like a human wrote it, not a bot. Natural rhythm, a little dry, maybe slightly pointed. No buzzword soup.

Reply with ONLY that one sentence, no preamble, no quotes."""


def translate(text: str) -> str:
    wrapped = f'The user is frustrated and wrote: "{text}"\nRewrite their message professionally.'
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": wrapped}
        ],
        max_tokens=80,
        temperature=1.2,
    )
    content = response.choices[0].message.content.strip()
    return next((line.strip() for line in content.splitlines() if line.strip()), content)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💼 *Corporate Translator Bot*\n\n"
        "Send me your raw, honest feelings about work, "
        "and I'll translate them into corporate-safe language.\n\n"
        "Try: _this meeting is a complete waste of time_\n\n"
        "Commands:\n"
        "/start — show this message\n"
        "/help — usage tips",
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "Just send any message and I'll rewrite it as corporate-speak.\n\n"
        "Works best with:\n"
        "• Workplace frustration\n"
        "• Meeting complaints\n"
        "• Feedback you can't actually send\n"
        "• Slack drafts before HR sees them"
    )


@dp.message()
async def handle(message: types.Message):
    if not message.text:
        return

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        translated = translate(message.text)
        await message.answer(
            f"💼 *Corporate version:*\n\n{translated}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"⚠️ Something broke: {str(e)}")


async def main():
    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
