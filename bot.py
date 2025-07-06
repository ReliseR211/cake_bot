from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

stores = ["Губкина", "Островского", "Ленина", "Бочкарева"]
big_cakes = ["Сникерс", "Шокобан", "Бархат", "Лес", "Генеральский", "Карабан", "Шоколадный", "Тропический", "Арахисовый взрыв"]
small_cakes = ["Сникерс", "Шокобан", "Лес", "Генеральский", "Шоколадный"]
target_stock = 2

inventory = {store: {"большие": {}, "маленькие": {}} for store in stores}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Команды:\n'
        '/остатки [магазин] [размер] [торт] [количество]\n'
        '/показать — остатки\n'
        '/заказ — общий заказ'
    )

async def update_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 4:
        await update.message.reply_text('Пример: /остатки Губкина большие Сникерс 1')
        return

    store, size, cake, qty_str = context.args[0], context.args[1].lower(), context.args[2], context.args[3]

    if store not in stores or size not in ["большие", "маленькие"]:
        await update.message.reply_text('Ошибка в данных.')
        return
    if size == "большие" and cake not in big_cakes:
        await update.message.reply_text('Такого большого торта нет.')
        return
    if size == "маленькие" and cake not in small_cakes:
        await update.message.reply_text('Такого маленького торта нет.')
        return

    try:
        qty = int(qty_str)
    except ValueError:
        await update.message.reply_text('Количество должно быть числом.')
        return

    inventory[store][size][cake] = qty
    need = max(0, target_stock - qty)
    await update.message.reply_text(f'{store}, {size} {cake}: {qty} шт. Нужно сделать: {need} шт.')

async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Сводка:\n"
    for store in stores:
        msg += f'\n🛒 {store}:\n  Большие:\n'
        for cake in big_cakes:
            qty = inventory[store]["большие"].get(cake, 0)
            need = max(0, target_stock - qty)
            msg += f'    {cake}: {qty} (Нужно: {need})\n'
        msg += "  Маленькие:\n"
        for cake in small_cakes:
            qty = inventory[store]["маленькие"].get(cake, 0)
            need = max(0, target_stock - qty)
            msg += f'    {cake}: {qty} (Нужно: {need})\n'
    await update.message.reply_text(msg)

async def total_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_big = {cake: 0 for cake in big_cakes}
    total_small = {cake: 0 for cake in small_cakes}

    for store in stores:
        for cake in big_cakes:
            qty = inventory[store]["большие"].get(cake, 0)
            total_big[cake] += max(0, target_stock - qty)
        for cake in small_cakes:
            qty = inventory[store]["маленькие"].get(cake, 0)
            total_small[cake] += max(0, target_stock - qty)

    msg = "Общий заказ:\nБольшие торты:\n"
    for cake, need in total_big.items():
        msg += f'  {cake}: {need} шт.\n'
    msg += "\nМаленькие торты:\n"
    for cake, need in total_small.items():
        msg += f'  {cake}: {need} шт.\n'

    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", update_inventory))
    app.add_handler(CommandHandler("show", show_inventory))
    app.add_handler(CommandHandler("order", total_order))
    app.run_polling()

if __name__ == '__main__':
    main()
