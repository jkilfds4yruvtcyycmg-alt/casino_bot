import asyncio
import logging
import random
import time
from collections import defaultdict

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import DiceEmoji
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats

# ⚠️ ВСТАВЬ СЮДА ТОКЕН ОТ БОТА КАЗИНО
BOT_TOKEN = "8888914933:AAH8AqXOZtvHjgZ-Q2oCb6XJ9g0Q36EiUf0"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ В ОПЕРАТИВКЕ ---
user_balances = defaultdict(lambda: 1000)
user_work_cd = {}
user_bonus_cd = {}

def get_valid_bet(user_id: int, arg: str) -> int:
    try:
        bet = int(arg)
        if bet <= 0:
            return 0
        if bet > user_balances[user_id]:
            return -1
        return bet
    except ValueError:
        return 0

# --- КОМАНДЫ И ИНФО ---

@dp.message(Command("help", "start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎰 ДОБРО ПОЖАЛОВАТЬ В ПОДПОЛЬНОЕ КАЗИНО! 🎲\n\n"
        "📜 **Базовые команды:**\n"
        "💰 /bal — Твой баланс\n"
        "⛏ /work — Поработать на заводе (раз в 10 мин)\n"
        "🎁 /bonus — Ежедневный бонус (раз в 24 часа)\n"
        "🏆 /top — Список самых богатых мажоров\n"
        "🔮 /ball <вопрос> — Магический Шар предсказаний\n\n"
        "🎮 **Игры на бабки:**\n"
        "🎰 /slots <ставка> — Однорукий бандит\n"
        "🎲 /dice <ставка> — Бросок костей\n"
        "🪙 /coin <ставка> <орел/решка> — Орёл или Решка\n"
        "🎯 /darts <ставка> — Бросок в мишень\n"
        "🥊 /fight <ставка> — Уличный бой с ботом\n"
        "🎳 /bowling <ставка> — Игра в боулинг\n\n"
        "💡 *Пример: /fight 100 или /ball Я сегодня разбогатею?*",
        parse_mode="Markdown"
    )

@dp.message(Command("bal", "balance"))
async def cmd_balance(message: types.Message):
    user_id = message.from_user.id
    bal = user_balances[user_id]
    await message.reply(f"💳 Твой баланс: **{bal:,}$**", parse_mode="Markdown")

@dp.message(Command("work"))
async def cmd_work(message: types.Message):
    user_id = message.from_user.id
    now = time.time()
    last_work = user_work_cd.get(user_id, 0)

    if now - last_work < 600:
        left = int(600 - (now - last_work))
        mins, secs = divmod(left, 60)
        await message.reply(f"⏳ Ты заебался на работе! Отдохни ещё {mins} мин {secs} сек.")
        return

    earned = random.randint(200, 800)
    user_balances[user_id] += earned
    user_work_cd[user_id] = now
    await message.reply(f"🛠 Ты отпахал смену на заводе и заработал +{earned}$!\nБаланс: **{user_balances[user_id]}$**")

# --- 1. ЕЖЕДНЕВНЫЙ БОНУС 🎁 ---
@dp.message(Command("bonus"))
async def cmd_bonus(message: types.Message):
    user_id = message.from_user.id
    now = time.time()
    last_bonus = user_bonus_cd.get(user_id, 0)

    if now - last_bonus < 86400:  # 24 часа
        left = int(86400 - (now - last_bonus))
        hours = left // 3600
        mins = (left % 3600) // 60
        await message.reply(f"⏳ Следующий ежедневный сундук доступен через {hours} ч {mins} мин!")
        return

    bonus = random.randint(500, 2500)
    user_balances[user_id] += bonus
    user_bonus_cd[user_id] = now
    await message.reply(f"🎁 Ты открыл ежедневный сундук и забрал +{bonus}$!\nБаланс: **{user_balances[user_id]}$**")

# --- 2.МАГИЧЕСКИЙ ШАР 🔮 ---

@dp.message(Command("ball"))
async def cmd_ball(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("🔮 Задай вопрос шару!")
        return

    answers = [
        "✅ Бесспорно, да!",
        "✅ 100% да, бро!",
        "❓ Пока не понятно, спроси позже...",
        "❌ Даже не думай!",
        "❌ Мой ответ - НЕТ."
    ]
    await message.reply(f"🔮 *Шар говорит:* {random.choice(answers)}")

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if not user_balances:
        await message.reply("Топ пуст, все бомжи!")
        return

    sorted_top = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]
    text = "🏆 *ТОП-5 МАЖОРОВ ЧАТА:*\n\n"

    for i, (u_id, bal) in enumerate(sorted_top, 1):
        text += f"{i}. User ID `{u_id}` - *{bal:,}$*\n"

    await message.reply(text, parse_mode="Markdown")

# --- ИГРЫ НА БАБКИ ---

# 🎰 СЛОТЫ
@dp.message(Command("slots"))
async def cmd_slots(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: /slots 100")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    user_balances[user_id] -= bet
    dice_msg = await message.answer_dice(emoji=DiceEmoji.SLOT_MACHINE)
    await asyncio.sleep(2)

    val = dice_msg.dice.value
    # В телеге 64 — это джекпот (три 777)
    if val == 64:
        win = bet * 10
        user_balances[user_id] += win
        await message.reply(f"🎰 **ДЖЕКПОТ! 777!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    elif val in [1, 22, 43]:
        win = bet * 2
        user_balances[user_id] += win
        await message.reply(f"🎰 **Совпадение!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await message.reply(f"🎰 Не повезло, ты проиграл **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# 🎲 КОСТИ
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: /dice 100")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    user_balances[user_id] -= bet
    dice_msg = await message.answer_dice(emoji=DiceEmoji.DICE)
    await asyncio.sleep(2)

    val = dice_msg.dice.value
    if val >= 4:
        win = bet * 2
        user_balances[user_id] += win
        await message.reply(f"🎲 Выпало **{val}**! Ты выиграл **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await message.reply(f"🎲 Выпало **{val}**! Ты проиграл **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# 🪙 ОРЕЛ ИЛИ РЕШКА
@dp.message(Command("coin"))
async def cmd_coin(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 3 or args[2].lower() not in ["орел", "решка"]:
        await message.reply("⚠️ Пример: /coin 100 орел (или решка)")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    choice = args[2].lower()
    user_balances[user_id] -= bet

    result = random.choice(["орел", "решка"])
    if choice == result:
        win = bet * 2
        user_balances[user_id] += win
        await message.reply(f"🪙 Выпал **{result.upper()}**! Ты угадал и забрал **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await message.reply(f"🪙 Выпал **{result.upper()}**! Ты не угадал и слил **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# 🎯 ДАРТС
@dp.message(Command("darts"))
async def cmd_darts(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: /darts 100")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    user_balances[user_id] -= bet
    anim_msg = await message.answer("🎯 Замахиваешься и бросаешь дротик...")
    await asyncio.sleep(1.5)

    score = random.randint(1, 6)
    if score == 6:
        win = bet * 3
        user_balances[user_id] += win
        await anim_msg.edit_text(f"🎯 **ПРЯМО В ЯБЛОЧКО!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    elif score in [4, 5]:
        win = int(bet * 1.5)
        user_balances[user_id] += win
        await anim_msg.edit_text(f"🎯 **Хороший бросок!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await anim_msg.edit_text(f"🎯 Мимо яблочка! Ты проиграл **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# 🥊 УЛИЧНЫЙ БОЙ
@dp.message(Command("fight"))
async def cmd_fight(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: /fight 100")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    user_balances[user_id] -= bet
    msg = await message.answer("🥊 Вышел на ринг против местного гопника...")
    await asyncio.sleep(1.5)

    if random.choice([True, False]):
        win = bet * 2
        user_balances[user_id] += win
        await msg.edit_text(f"🥊 **Ты вырубил соперника с вертухи!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await msg.edit_text(f"🥊 **Тебе прописали двоичку и отобрали бабки!**\nПотеряно: **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# 🎳 БОУЛИНГ
@dp.message(Command("bowling"))
async def cmd_bowling(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: /bowling 100")
        return

    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке или недостаточно средств!")
        return

    user_balances[user_id] -= bet
    dice_msg = await message.answer_dice(emoji=DiceEmoji.BOWLING)
    await asyncio.sleep(2)

    val = dice_msg.dice.value
    if val == 6:
        win = bet * 3
        user_balances[user_id] += win
        await message.reply(f"🎳 **СТРАЙК! Выбил все кегли!**\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    elif val >= 3:
        win = int(bet * 1.5)
        user_balances[user_id] += win
        await message.reply(f"🎳 Сбил несколько кеглей!\nВыигрыш: **+{win}$**!\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await message.reply(f"🎳 Шар улетел в желоб! Ты проиграл **-{bet}$**.\nБаланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# --- ЗАПУСК БОТА ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
