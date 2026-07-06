import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language mapping for 69 languages (expanded list)
# Based on Telegram bot standards for translation support [citation:1][citation:2]
LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian",
    "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan",
    "ceb": "Cebuano", "ny": "Chichewa", "zh-cn": "Chinese Simplified",
    "zh-tw": "Chinese Traditional", "co": "Corsican", "hr": "Croatian",
    "cs": "Czech", "da": "Danish", "nl": "Dutch", "en": "English",
    "eo": "Esperanto", "et": "Estonian", "tl": "Filipino", "fi": "Finnish",
    "fr": "French", "fy": "Frisian", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "ht": "Haitian Creole",
    "ha": "Hausa", "haw": "Hawaiian", "he": "Hebrew", "hi": "Hindi",
    "hmn": "Hmong", "hu": "Hungarian", "is": "Icelandic", "ig": "Igbo",
    "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "jw": "Javanese", "kn": "Kannada", "kk": "Kazakh", "km": "Khmer",
    "rw": "Kinyarwanda", "ko": "Korean", "ku": "Kurdish", "ky": "Kyrgyz",
    "lo": "Lao", "la": "Latin", "lv": "Latvian", "lt": "Lithuanian",
    "lb": "Luxembourgish", "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese", "mi": "Maori", "mr": "Marathi",
    "mn": "Mongolian", "my": "Myanmar", "ne": "Nepali", "no": "Norwegian",
    "or": "Odia", "ps": "Pashto", "fa": "Persian", "pl": "Polish",
    "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian", "ru": "Russian",
    "sm": "Samoan", "gd": "Scots Gaelic", "sr": "Serbian", "st": "Sesotho",
    "sn": "Shona", "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "es": "Spanish", "su": "Sundanese",
    "sw": "Swahili", "sv": "Swedish", "tg": "Tajik", "ta": "Tamil",
    "tt": "Tatar", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh", "xh": "Xhosa",
    "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu"
}

# User language preferences storage (in production, use a database)
user_preferences = {}

# Translation function using MyMemory API (free, no API key required) [citation:9]
import requests
import json

def translate_text(text, target_lang, source_lang="auto"):
    """Translate text using MyMemory API - free and works without API key"""
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}",
        "de": "your_email@example.com"  # Replace with your email for higher limits
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("responseStatus") == 200:
            return data.get("responseData", {}).get("translatedText", "Translation failed")
        else:
            return f"Error: {data.get('responseDetails', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"Translation error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with language selection"""
    keyboard = [
        [InlineKeyboardButton("🌍 Select Language", callback_data="select_lang")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 Welcome to Language 69 Translator Bot!\n\n"
        "Send me any text and I'll translate it to your chosen language.\n"
        "Use /setlang to change your preferred language.\n"
        "Available: 69 languages! 🌍",
        reply_markup=reply_markup
    )

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Let user choose their translation target language"""
    keyboard = []
    # Show a subset of languages to avoid overwhelming the user
    popular_langs = ["en", "es", "fr", "de", "zh-cn", "ja", "ar", "ru", "pt", "it", "hi", "ko"]
    
    row = []
    for i, code in enumerate(popular_langs):
        row.append(InlineKeyboardButton(LANGUAGES.get(code, code), callback_data=f"lang_{code}"))
        if len(row) == 3:  # 3 buttons per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("📚 See All 69 Languages", callback_data="show_all_langs")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 Select your translation target language:",
        reply_markup=reply_markup
    )

async def show_all_langs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all 69 available languages"""
    query = update.callback_query
    await query.answer()
    
    lang_list = "\n".join([f"• {name} (`{code}`)" for code, name in sorted(LANGUAGES.items())])
    await query.edit_message_text(
        f"📚 **All 69 Supported Languages:**\n\n{lang_list}\n\n"
        "Use /setlang to set your preferred language.",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "select_lang":
        await set_lang(update, context)
        return
    
    if data == "help":
        await query.edit_message_text(
            "ℹ️ **How to use:**\n\n"
            "1. Set your target language with /setlang\n"
            "2. Send any text message\n"
            "3. Bot replies with translation!\n\n"
            "Commands:\n"
            "/start - Welcome\n"
            "/setlang - Change language\n"
            "/help - This help",
            parse_mode="Markdown"
        )
        return
    
    if data == "show_all_langs":
        await show_all_langs(update, context)
        return
    
    if data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        user_id = update.effective_user.id
        user_preferences[user_id] = lang_code
        
        await query.edit_message_text(
            f"✅ Language set to: **{LANGUAGES.get(lang_code, lang_code)}**\n\n"
            f"Now send me any text to translate!",
            parse_mode="Markdown"
        )

async def translate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate incoming text messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    target_lang = user_preferences.get(user_id, "en")
    
    # Show user what's happening
    status_msg = await update.message.reply_text("🔄 Translating...")
    
    translated = translate_text(text, target_lang)
    
    await status_msg.delete()
    await update.message.reply_text(
        f"🌍 **Translation ({LANGUAGES.get(target_lang, target_lang)}):**\n\n{translated}",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "ℹ️ **Language 69 Translator Bot**\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/setlang - Choose your target language\n"
        "/help - This help\n\n"
        "Just send any text and I'll translate it to your selected language!",
        parse_mode="Markdown"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "❌ Unknown command. Use /help for available commands."
    )

def main():
    """Start the bot using long polling mode [citation:3][citation:11]"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlang", set_lang))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Start long polling - no webhook URL needed [citation:3]
    logger.info("Starting bot with long polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
