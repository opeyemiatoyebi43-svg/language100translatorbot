# Language 100 Translator Bot 🤖

A Telegram bot that translates text between 100+ languages.

## Features
- Auto-detect source language and translate to your preferred target language
- Set custom target language using `/setlang`
- Manual translation with source/target specification using `/translate`
- Support for 100+ languages

## Deployment
This bot is deployed on Railway with GitHub integration.

## Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/setlang [code]` - Set your preferred target language
- `/languages` - Show all available languages
- `/translate [src] [tgt] [text]` - Manual translation
- Send any text - Auto-translate to your preferred language

## Environment Variables
- `TELEGRAM_TOKEN` - Your bot token from BotFather
