import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from tinydb import TinyDB, Query
from datetime import datetime

TOKEN = 'TU_TOKEN_DE_BOT'
DB_PATH = 'users.json'

db = TinyDB(DB_PATH)
User = Query()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def generate_code():
    """Simula la generación de un código de 6 dígitos."""
    from random import randint
    return str(randint(100000, 999999))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Busca si ya está en la base de datos
    user = db.get(User.user_id == user_id)
    if not user:
        db.insert({'user_id': user_id, 'enabled': False, 'codes_today': 0, 'last_date': '', 'username': update.effective_user.username})
    await update.message.reply_text(
        f"¡Hola! Tu ID de usuario es: {user_id}\n\n"
        "Envíale este ID a tu administrador para que te active la generación de códigos.\n"
        "Cuando te activen, podrás pedir hasta 3 códigos por día usando /codigo"
    )

async def codigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get(User.user_id == user_id)
    if not user:
        await update.message.reply_text("Debes usar /start primero.")
        return

    if not user['enabled']:
        await update.message.reply_text("Tu usuario aún no está habilitado. Envíale tu ID al administrador.")
        return

    # Resetea el conteo si es otro día
    today = datetime.now().strftime('%Y-%m-%d')
    if user.get('last_date', '') != today:
        db.update({'codes_today': 0, 'last_date': today}, User.user_id == user_id)
        user = db.get(User.user_id == user_id)

    if user['codes_today'] >= 3:
        await update.message.reply_text("Has alcanzado el límite de 3 códigos diarios. Intenta mañana.")
        return

    code = generate_code()
    db.update({'codes_today': user['codes_today'] + 1, 'last_date': today}, User.user_id == user_id)
    await update.message.reply_text(f"Tu código de acceso es: {code}")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Obtener tu ID de usuario\n"
        "/codigo - Solicitar código (máx. 3 por día)\n"
        "/ayuda - Mostrar este mensaje"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("codigo", codigo))
    app.add_handler(CommandHandler("ayuda", ayuda))
    print("Bot corriendo...")
    app.run_polling()
