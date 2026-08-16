
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
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА_КАЗИНО"

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
        "🎰 **ДОБРО ПОЖАЛОВАТЬ В ПОДПОЛЬНОЕ КАЗИНО!** 🎲\n\n"
        "📜 **Базовые команды:**\n"
        "💰 `/bal` — Твой баланс\n"
        "⛏ `/work` — Поработать на заводе (раз в 10 мин)\n"
        "🎁 `/bonus` — Ежедневный бонус (раз в 24 часа)\n"
        "🏆 `/top` — Список самых богатых мажоров\n"
        "🔮 `/ball <вопрос>` — Магический Шар предсказаний\n\n"
        "🎮 **Игры на бабки:**\n"
        "🎰 `/slots <ставка>` — Однорукий бандит\n"
        "🎲 `/dice <ставка>` — Бросок костей\n"
        "🪙 `/coin <ставка> <орел/решка>` — Орёл или Решка\n"
        "🎯 `/darts <ставка>` — Бросок в мишень\n"
        "🥊 `/fight <ставка>` — Уличный бой с ботом\n"
        "🎳 `/bowling <ставка>` — Игра в боулинг\n\n"
        "💡 *Пример: `/fight 100` или `/ball Я сегодня разбогатею?`*",
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
        await message.reply(f"⏳ Ты заебался на работе! Отдохни ещё **{mins} мин {secs} сек**.")
        return

    earned = random.randint(200, 800)
    user_balances[user_id] += earned
    user_work_cd[user_id] = now
    await message.reply(f"🛠 Ты отпахал смену на заводе и заработал **+{earned}$**!\nБаланс: **{user_balances[user_id]}$**")

# --- 1. ЕЖЕДНЕВНЫЙ БОНУС 🎁 ---
@dp.message(Command("bonus"))
async def cmd_bonus(message: types.Message):
    user_id = message.from_user.id
    now = time.time()
    last_bonus = user_bonus_cd.get(user_id, 0)

    if now - last_bonus < 86400: # 24 часа
        left = int(86400 - (now - last_bonus))
        hours = left // 3600
        mins = (left % 3600) // 60
        await message.reply(f"⏳ Следующий ежедневный сундук доступен через **{hours} ч {mins} мин**!")
        return

    bonus = random.randint(500, 2500)
    user_balances[user_id] += bonus
    user_bonus_cd[user_id] = now
    await message.reply(f"🎁 Ты открыл ежедневный сундук и забрал **+{bonus}$**!\nБаланс: **{user_balances[user_id]}$**")

# --- 2. МАГИЧЕСКИЙ ШАР 🔮 ---
@dp.message(Command("ball"))
async def cmd_ball(message: types.Message):
    args = message.text.split(maxsplit=1)
if len(args) < 2:
        await message.reply("🔮 Задай вопрос шару! Пример: `/ball Бот нормальный?`", parse_mode="Markdown")
        return
    
    answers = [
        "✅ Бесспорно, да!", "✅ 100% да, бро!", "✅ Знаки говорят — ДА.",
        "❓ Пока не понятно, спроси позже...", "❓ Лучше тебе этого не знать...",
        "❌ Даже не думай!", "❌ Мой ответ — НЕТ.", "❌ Шансы равны нулю!"
    ]
    await message.reply(f"🔮 **Шар говорит:** {random.choice(answers)}")

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    if not user_balances:
        await message.reply("Топ пуст, все бомжи!")
        return
    
    sorted_top = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]
    text = "🏆 **ТОП-5 МАЖОРОВ ЧАТА:**\n\n"
    
    for i, (u_id, bal) in enumerate(sorted_top, 1):
        text += f"{i}. User ID `{u_id}` — **{bal:,}$**\n"
        
    await message.reply(text, parse_mode="Markdown")

# --- ИГРЫ НА БАБКИ ---

# 3. УЛИЧНЫЙ БОЙ 🥊
@dp.message(Command("fight"))
async def cmd_fight(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("🥊 Напиши ставку! Пример: `/fight 100`", parse_mode="Markdown")
        return
        
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Неверная ставка или не хватает денег!")
        return

    user_balances[user_id] -= bet
    anim_msg = await message.answer("🥊 *Выходите на ринг... Оппонент разминает кулаки...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)
    
    user_hp = random.randint(50, 100)
    bot_hp = random.randint(50, 100)
    
    if user_hp > bot_hp:
        win = bet * 2
        user_balances[user_id] += win
        await anim_msg.edit_text(
            f"🥊 💥 **ТЫ НОКАУТИРОВАЛ СОПЕРНИКА!**\n\n"
            f"💪 Твоё ХП: {user_hp} | ХП Врага: {bot_hp}\n"
            f"💰 Твой выигрыш: **+{win}$**!\n"
            f"💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown"
        )
    else:
        await anim_msg.edit_text(
            f"🥊 🤕 **ТЕБЕ НАВЕСИЛИ ЛЮЛЕЙ И ОТЖАЛИ БАБКИ!**\n\n"
            f"📉 Твоё ХП: {user_hp} | ХП Врага: {bot_hp}\n"
            f"💸 Потеряно: **-{bet}$**\n"
            f"💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown"
        )

# 4. БОУЛИНГ 🎳
@dp.message(Command("bowling"))
async def cmd_bowling(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("🎳 Напиши ставку! Пример: `/bowling 100`", parse_mode="Markdown")
        return
        
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Неверная ставка или не хватает денег!")
        return

    user_balances[user_id] -= bet
    anim_msg = await message.answer("🎳 *Бросаешь шар по дорожке...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)
    
    pins = random.randint(0, 6) # 6 - Страйк
    if pins == 6:
        win = bet * 3
        user_balances[user_id] += win
        await anim_msg.edit_text(
            f"🎳 ⚡️ **СТРАЙК! СБИТЫ ВСЕ КЕГЛИ!** (x3)\n\n"
            f"💰 Выигрыш: **+{win}$**!\n"
            f"💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown"
        )
    elif pins in [3, 4, 5]:
        win = int(bet * 1.5)
        user_balances[user_id] += win
        await anim_msg.edit_text(
            f"🎳 **Сбил {pins} кеглей!** (x1.5)\n\n"
            f"💰 Выигрыш: **+{win}$**!\n"
            f"💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown"
        )
    else:
        await anim_msg.edit_text(
            f"🎳 💨 **Шар улетел в желоб! Сбито кеглей: {pins}**\n\n"
            f"📉 Потеряно: **-{bet}$**\n"
            f"💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown"
        )

# СЛОТЫ 🎰
@dp.message(Command("slots"))
async def cmd_slots(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: `/slots 100`
", parse_mode="Markdown")
        return
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке!")
        return

    user_balances[user_id] -= bet
    msg = await message.answer_dice(emoji=DiceEmoji.SLOT_MACHINE)
    await asyncio.sleep(2)

    val = msg.dice.value
    if val == 64:
        win = bet * 10
        user_balances[user_id] += win
        await message.reply(f"💥 **ДЖЕКПОТ! 7-7-7!** 💥\nТы выиграл **+{win}$**!", parse_mode="Markdown")
    elif val in [1, 22, 43]:
        win = bet * 3
        user_balances[user_id] += win
        await message.reply(f"🎉 **ТРИ В РЯД!** Выигрыш: **+{win}$**!", parse_mode="Markdown")
    else:
        await message.reply(f"📉 Не повезло, бро! Минус **-{bet}$**.")

# КОСТИ 🎲
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Напиши ставку! Пример: `/dice 100`", parse_mode="Markdown")
        return
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Ошибка в ставке!")
        return

    user_balances[user_id] -= bet
    await message.answer("🎲 Бросаешь ты...")
    user_dice = await message.answer_dice(emoji=DiceEmoji.DICE)
    await asyncio.sleep(2)
    
    await message.answer("🎲 Бросает казино...")
    bot_dice = await message.answer_dice(emoji=DiceEmoji.DICE)
    await asyncio.sleep(2)

    u_val = user_dice.dice.value
    b_val = bot_dice.dice.value

    if u_val > b_val:
        win = bet * 2
        user_balances[user_id] += win
        await message.reply(f"🎉 Ты выбросил **{u_val}**, казино **{b_val}**.\nТы ПОБЕДИЛ и забрал **+{win}$**!")
    elif u_val < b_val:
        await message.reply(f"🗿 Ты выбросил **{u_val}**, казино **{b_val}**.\nТы проиграл **-{bet}$**!")
    else:
        user_balances[user_id] += bet
        await message.reply(f"🤝 Ничья! Оба выбросили **{u_val}**. Ставка возвращена.")

# МОНЕТКА 🪙
@dp.message(Command("coin"))
async def cmd_coin(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 3 or args[2].lower() not in ["орел", "решка"]:
        await message.reply("⚠️ Введи ставку и выбор! Пример: `/coin 100 орел`", parse_mode="Markdown")
        return
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Недостаточно средств или неверная ставка!")
        return

    user_choice = args[2].lower()
    user_balances[user_id] -= bet
    result = random.choice(["орел", "решка"])
    
    if user_choice == result:
        win = bet * 2
        user_balances[user_id] += win
        await message.reply(f"🪙 Выпал(а) **{result.upper()}**!\nТы угадал и получил **+{win}$**!", parse_mode="Markdown")
    else:
        await message.reply(f"🪙 Выпал(а) **{result.upper()}**!\nТы не угадал. Минус **-{bet}$**.", parse_mode="Markdown")

# ДАРТС 🎯
@dp.message(Command("darts"))
async def cmd_darts(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply("🎯 Напиши ставку цифрой! Пример: `/darts 100`", parse_mode="Markdown")
        return
    bet = get_valid_bet(user_id, args[1])
    if bet <= 0:
        await message.reply("❌ Неверная ставка!")
        return

    user_balances[user_id] -= bet
    anim_msg = await message.answer("🎯 *Замахиваешься и бросаешь дротик...* 🎯", parse_mode="Markdown")
    await asyncio.sleep(1.5)
    
    score = random.randint(1, 6)
    if score == 6:
        win = bet * 3
        user_balances[user_id] += win
        await anim_msg.edit_text(f"🎯 🎯 🎯 **ПРЯМО В ЯБЛОЧКО! (100/100)** 🎯 🎯 🎯\n\n🔥 Множитель: **x3**\n💰 Выигрыш: **+{win}$**!\n💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown")
    elif score in [4, 5]:
        win = int(bet * 1.5)
        user_balances[user_id] += win
        await anim_msg.edit_text(f"🎯 **ОТЛИЧНЫЙ БРОСОК! (Попал в красную зону)**\n\n✨ Множитель: **x1.5**\n💰 Выигрыш: **+{win}$**!\n💳 Баланс: **{use
r_balances[user_id]}$**", parse_mode="Markdown")
    else:
        await anim_msg.edit_text(f"🎯 💨 **МИМО ЯБЛОЧКА! (Дротик воткнулся в стену)**\n\n📉 Потеряно: **-{bet}$**\n💳 Баланс: **{user_balances[user_id]}$**", parse_mode="Markdown")

# --- УСТАНОВКА ВСПЛЫВАЮЩЕГО МЕНЮ КОМАНД ---
async def set_main_menu(bot: Bot):
    main_commands = [
        BotCommand(command="help", description="📜 Список всех команд"),
        BotCommand(command="bal", description="💰 Посмотреть свой баланс"),
        BotCommand(command="work", description="⛏ Поработать на заводе"),
        BotCommand(command="bonus", description="🎁 Ежедневный подарок"),
        BotCommand(command="top", description="🏆 Топ богачей чата"),
        BotCommand(command="fight", description="🥊 Уличный бой с ботом"),
        BotCommand(command="bowling", description="🎳 Игра в боулинг"),
        BotCommand(command="slots", description="🎰 Однорукий бандит"),
        BotCommand(command="dice", description="🎲 Игра в кости"),
        BotCommand(command="coin", description="🪙 Игра в монетку"),
        BotCommand(command="darts", description="🎯 Бросок в мишень"),
        BotCommand(command="ball", description="🔮 Магический шар ответов"),
    ]
    await bot.set_my_commands(main_commands, scope=BotCommandScopeAllGroupChats())

async def main():
    print("Казино и игры запущены, меню обновлено!")
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
