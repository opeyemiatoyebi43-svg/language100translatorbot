import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from googletrans import Translator, LANGUAGES
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Language codes for the most common 100 languages
LANGUAGE_CODES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
    'bn': 'Bengali', 'ur': 'Urdu', 'fa': 'Persian', 'tl': 'Tagalog',
    'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian', 'ms': 'Malay',
    'ne': 'Nepali', 'sw': 'Swahili', 'ha': 'Hausa', 'yo': 'Yoruba',
    'ig': 'Igbo', 'zu': 'Zulu', 'af': 'Afrikaans', 'am': 'Amharic',
    'az': 'Azerbaijani', 'be': 'Belarusian', 'bg': 'Bulgarian', 'bs': 'Bosnian',
    'ca': 'Catalan', 'ceb': 'Cebuano', 'co': 'Corsican', 'cs': 'Czech',
    'cy': 'Welsh', 'da': 'Danish', 'el': 'Greek', 'eo': 'Esperanto',
    'et': 'Estonian', 'eu': 'Basque', 'fi': 'Finnish', 'fy': 'Frisian',
    'ga': 'Irish', 'gd': 'Scottish Gaelic', 'gl': 'Galician', 'gu': 'Gujarati',
    'haw': 'Hawaiian', 'he': 'Hebrew', 'hmn': 'Hmong', 'hr': 'Croatian',
    'ht': 'Haitian Creole', 'hu': 'Hungarian', 'hy': 'Armenian', 'is': 'Icelandic',
    'jw': 'Javanese', 'ka': 'Georgian', 'kk': 'Kazakh', 'km': 'Khmer',
    'kn': 'Kannada', 'ku': 'Kurdish', 'ky': 'Kyrgyz', 'la': 'Latin',
    'lb': 'Luxembourgish', 'lo': 'Lao', 'lt': 'Lithuanian', 'lv': 'Latvian',
    'mg': 'Malagasy', 'mi': 'Maori', 'mk': 'Macedonian', 'ml': 'Malayalam',
    'mn': 'Mongolian', 'mr': 'Marathi', 'mt': 'Maltese', 'my': 'Burmese',
    'ny': 'Chichewa', 'or': 'Odia', 'pa': 'Punjabi', 'pl': 'Polish',
    'ps': 'Pashto', 'ro': 'Romanian', 'rw': 'Kinyarwanda', 'sd': 'Sindhi',
    'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'sm': 'Samoan',
    'sn': 'Shona', 'so': 'Somali', 'sq': 'Albanian', 'sr': 'Serbian',
    'st': 'Sesotho', 'su': 'Sundanese', 'sv': 'Swedish', 'ta': 'Tamil',
    'te': 'Telugu', 'tg': 'Tajik', 'tr': 'Turkish', 'uk': 'Ukrainian',
    'uz': 'Uzbek', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba'
}

# User preferences storage (in-memory)
user_languages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = f"""
🌟 *Welcome to Language 100 Translator Bot, {user.first_name}!* 🌟

I can translate text between 100+ languages.

*Commands:*
/translate - Translate text to your preferred language
/setlang - Set your preferred target language
/languages - See all available languages
/help - Show this help message

*How to use:*
1. Simply send me any text and I'll auto-detect and translate it to your preferred language
2. Use /setlang to change your target language (default is English)
3. Use /translate to manually choose source and target languages

Start by sending me any text to translate! 🚀
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = """
📖 *Help Guide*

*Basic Usage:*
• Send any text → I'll auto-detect and translate to your preferred language
• Use /setlang → Change your target language
• Use /translate → Source → Target translation

*Examples:*
• Send "Hello world" → Translates to your preferred language
• Use /translate en es [text] → Translates from English to Spanish
• Use /languages → Shows all supported languages

*Tips:*
• Your preferred language is saved for future translations
• Use language codes like: en, es, fr, de, ja, zh-cn, etc.

Need help? Just ask! 😊
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user's preferred target language."""
    user_id = update.effective_user.id
    
    # If no args provided, show current language
    if not context.args:
        current = user_languages.get(user_id, 'en')
        await update.message.reply_text(
            f"🌐 Your current target language is: *{LANGUAGE_CODES.get(current, current)}* ({current})\n\n"
            f"To change it, use: /setlang [language_code]\n"
            f"Example: /setlang es\n"
            f"Use /languages to see all available codes.",
            parse_mode='Markdown'
        )
        return
    
    # Set new language
    new_lang = context.args[0].lower()
    if new_lang in LANGUAGE_CODES:
        user_languages[user_id] = new_lang
        await update.message.reply_text(
            f"✅ Language set to: *{LANGUAGE_CODES[new_lang]}* ({new_lang})",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ Language code '{new_lang}' not supported.\n"
            f"Use /languages to see all available codes."
        )

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available languages."""
    # Split languages into pages (20 per page)
    lang_list = sorted(LANGUAGE_CODES.items())
    chunks = [lang_list[i:i+20] for i in range(0, len(lang_list), 20)]
    
    for i, chunk in enumerate(chunks, 1):
        message = f"🌍 *Languages (Page {i}/{len(chunks)})*\n\n"
        for code, name in chunk:
            message += f"• `{code}` → {name}\n"
        
        if i == 1:
            message += "\nUse /setlang [code] to set your target language."
        
        await update.message.reply_text(message, parse_mode='Markdown')

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate received text."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Get user's preferred language (default: English)
    target_lang = user_languages.get(user_id, 'en')
    
    try:
        # Auto-detect source and translate
        translated = translator.translate(text, dest=target_lang)
        
        # Get source language name
        src_lang_name = LANGUAGE_CODES.get(translated.src, translated.src)
        tgt_lang_name = LANGUAGE_CODES.get(target_lang, target_lang)
        
        response = f"""
🔤 *Translation Results*
━━━━━━━━━━━━━━━━━━

📥 *Original* ({src_lang_name}):
{text}

📤 *Translated* ({tgt_lang_name}):
{translated.text}

━━━━━━━━━━━━━━━━━━
💡 Send any text to translate to your preferred language!
Use /setlang to change target language.
"""
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't translate that text. Please try again.\n"
            "Make sure the text is supported by Google Translate."
        )

async def manual_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual translation with source and target language."""
    args = context.args
    
    if len(args) < 3:
        await update.message.reply_text(
            "❌ *Usage:* /translate [source_lang] [target_lang] [text]\n\n"
            "Example: /translate en es Hello\n"
            "Example: /translate auto fr Bonjour\n\n"
            "Use /languages to see language codes.",
            parse_mode='Markdown'
        )
        return
    
    source_lang = args[0]
    target_lang = args[1]
    text = ' '.join(args[2:])
    
    if target_lang not in LANGUAGE_CODES and target_lang != 'auto':
        await update.message.reply_text(
            f"❌ Target language '{target_lang}' not supported. Use /languages to see all codes."
        )
        return
    
    try:
        translated = translator.translate(text, src=source_lang, dest=target_lang)
        
        src_name = LANGUAGE_CODES.get(translated.src, translated.src)
        tgt_name = LANGUAGE_CODES.get(target_lang, target_lang)
        
        response = f"""
🔤 *Manual Translation*
━━━━━━━━━━━━━━━━━━

📥 *Original* ({src_name}):
{text}

📤 *Translated* ({tgt_name}):
{translated.text}

━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Manual translation error: {e}")
        await update.message.reply_text(
            "❌ Translation failed. Please check your language codes and try again."
        )

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("No TELEGRAM_TOKEN found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setlang", set_language))
    application.add_handler(CommandHandler("languages", show_languages))
    application.add_handler(CommandHandler("translate", manual_translate))
    
    # Handle all text messages for translation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
