import discord
import os
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Файл для хранения данных
DATA_FILE = "economy_data.json"

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"balances": {}, "daily_cooldowns": {}}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(bot.economy_data, f)

@bot.event
async def on_ready():
    bot.economy_data = load_data()
    print(f'💰 Экономика бот {bot.user} запущен!')

@bot.command()
async def баланс(ctx):
    user_id = str(ctx.author.id)
    balance = bot.economy_data["balances"].get(user_id, 0)
    await ctx.send(f'💰 **Баланс {ctx.author.mention}:** {balance} монет')

@bot.command()
async def ежедневно(ctx):
    user_id = str(ctx.author.id)
    now = datetime.now().timestamp()
    
    # Проверка кулдауна
    last_daily = bot.economy_data["daily_cooldowns"].get(user_id, 0)
    cooldown = 24 * 60 * 60  # 24 часа в секундах
    
    if now - last_daily < cooldown:
        remaining = cooldown - (now - last_daily)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await ctx.send(f'⏰ Уже получали награду! Следующая через: {hours}ч {minutes}м')
        return
    
    # Выдача награды
    reward = 100
    bot.economy_data["balances"][user_id] = bot.economy_data["balances"].get(user_id, 0) + reward
    bot.economy_data["daily_cooldowns"][user_id] = now
    
    save_data()
    await ctx.send(f'🎁 **Ежедневная награда!** +{reward} монет!\n💰 Теперь у вас: {bot.economy_data["balances"][user_id]} монет')

@bot.command()
async def работа(ctx):
    user_id = str(ctx.author.id)
    salary = 50
    bot.economy_data["balances"][user_id] = bot.economy_data["balances"].get(user_id, 0) + salary
    save_data()
    await ctx.send(f'💼 **Работа выполнена!** +{salary} монет!\n💰 Теперь у вас: {bot.economy_data["balances"][user_id]} монет')

@bot.command()
async def перевод(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send('❌ Сумма должна быть положительной!')
        return
        
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)
    
    if bot.economy_data["balances"].get(sender_id, 0) < amount:
        await ctx.send('❌ Недостаточно средств!')
        return
    
    # Перевод
    bot.economy_data["balances"][sender_id] = bot.economy_data["balances"].get(sender_id, 0) - amount
    bot.economy_data["balances"][receiver_id] = bot.economy_data["balances"].get(receiver_id, 0) + amount
    
    save_data()
    await ctx.send(f'✅ **Перевод выполнен!**\n📤 {ctx.author.mention} → {member.mention}\n💰 Сумма: {amount} монет')

@bot.command()
async def топ(ctx):
    balances = bot.economy_data["balances"]
    top_users = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 ТОП 10 БОГАЧЕЙ", color=0x00ff00)
    for i, (user_id, balance) in enumerate(top_users, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{i}. {user.name}", value=f"{balance} монет", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def магазин(ctx):
    embed = discord.Embed(title="🛒 МАГАЗИН", color=0xffd700)
    embed.add_field(name="🎮 Игра", value="100 монет", inline=True)
    embed.add_field(name="🎭 Роль", value="200 монет", inline=True)
    embed.add_field(name="💎 Премиум", value="500 монет", inline=True)
    embed.add_field(name="🛍️ Как купить", value="Скоро будет реализовано!", inline=False)
    await ctx.send(embed=embed)

bot.run(os.environ['DISCORD_TOKEN'])
