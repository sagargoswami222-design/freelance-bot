"""
Freelance Helper Telegram Bot
With Groq AI Integration (FREE!)
"""
import os
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler,
MessageHandler, filters, ContextTypes
import requests
# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.INFO)
logger = logging.getLogger(__name__)
# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_GROQ_KEY_HERE')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0')) # Your Telegram user ID
# Demo tasks
DEMO_TASKS = [
{
"id": 1,
"title": "Write Product Review - Coffee Maker",
"platform": "MTurk",
"pay": "$5.00",
"time": "15 min",
"category": "writing",
"link": "https://worker.mturk.com/projects/example1", "category": "data",
"link": "https://workplace.clickworker.com/jobs/example2",
"desc": "Enter product details"
},
{
"id": 3,
"title": "Translate English to Hindi",
"platform": "Microworkers",
"pay": "$3.50",
"time": "10 min",
"category": "translation",
"link": "https://microworkers.com/view_job.php?id=example3", "id": 4,
"title": "Survey - Shopping Habits",
"platform": "MTurk",
"pay": "$2.50",
"time": "8 min",
"category": "survey",
"link": "https://worker.mturk.com/projects/example4",
"desc": "Answer 15 questions"
},
{
"id": 5,
"title": "Image Description Task",
"platform": "Fiverr",
"pay": "$3.00",
"time": "12 min",
"category": "writing",
"link": "https://fiverr.com/gigs/example5",
"desc": "Describe 10 images in 30 words each"
}
]
# User stats storage
user_stats = {}
# Security: Check authorized user
def is_authorized(user_id: int) -> bool:
if ADMIN_USER_ID == 0:
return True # First time setup
return user_id == ADMIN_USER_ID # Groq AI integration
def call_groq_ai(prompt: str, max_tokens: int = 500) -> str:
try:
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
"Authorization": f"Bearer {GROQ_API_KEY}",
"Content-Type": "application/json"
}
data = {
"model": "llama-3.1-70b-versatile",
"messages": [{"role": "user", "content": prompt}],
"max_tokens": max_tokens,
"temperature": 0.7
}
response = requests.post(url, headers=headers, json=data, timeout=30)
if response.status_code == 200:
result = response.json()
return result['choices'][0]['message']['content'].strip() else:
logger.error(f"Groq API error: {response.status_code}")
return "❌ AI service temporarily unavailable. Please try again."
except Exception as e:
logger.error(f"Groq API exception: {e}")
return "❌ Error connecting to AI. Please try again later."
# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
user_id = user.id
if not is_authorized(user_id):
await update.message.reply_text("⛔ Unauthorized access. This bot is
private.")
return
welcome_text = f"""
👋 **Welcome {user.first_name}!**
🤖 **Freelance Helper Bot** - Your AI-powered task assistant! **Commands:**
/findtasks - Search for new tasks
/help - Get AI assistance
/stats - View your earnings
/settings - Bot preferences
**Quick Start:**
󰍹 Use /findtasks to see available tasks
󰍽 Click task links to open
󰍼 Use /help for AI assistance
󰍶 Track earnings with /stats
🚀 Let's start earning!
"""
await update.message.reply_text(welcome_text, parse_mode='Markdown')
async def find_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
if not is_authorized(user_id):
await update.message.reply_text("⛔ Unauthorized")
return
# Send searching message
msg = await update.message.reply_text("🔍 Searching for tasks across
platforms...")
# Filter tasks
filter_category = context.args[0] if context.args else None
if filter_category:
tasks = [t for t in DEMO_TASKS if t['category'] == filter_category]
category_text = f" ({filter_category})"
else:
tasks = DEMO_TASKS category_text = ""
# Format response
response = f"✅ **Found {len(tasks)} Tasks{category_text}!**\n\n"
for i, task in enumerate(tasks[:5], 1):
response += f"**{i}️⃣{task['title']}
response += f"💰 {task['pay']} • {task['time']} • {task['platform']}\n"
response += f"📝 {task['desc']}\n\n"
# Buttons
keyboard = [
[
InlineKeyboardButton("🔗 Open Task", url=task['link']),
InlineKeyboardButton("💡 AI Help",
callback_data=f"help_{task['id']}")
],
[
InlineKeyboardButton("⭐ Save", callback_data=f"save_{task['id']}"),
InlineKeyboardButton("✅ Mark Done",
callback_data=f"done_{task['id']}")
]
]
reply_markup = InlineKeyboardMarkup(keyboard)
await context.bot.send_message(
chat_id=update.effective_chat.id,
text=response,
reply_markup=reply_markup,
parse_mode='Markdown'
)
response = ""
await msg.delete()
# Navigation
nav_keyboard = [
[
InlineKeyboardButton("🔄 Refresh", callback_data="refresh_tasks"),
InlineKeyboardButton("🎯 Filter", callback_data="filter_tasks")
]
]
await context.bot.send_message(
chat_id=update.effective_chat.id,
text="📋 **More options:**",
reply_markup=InlineKeyboardMarkup(nav_keyboard),
parse_mode='Markdown'
)
async def ai_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id if not is_authorized(user_id): await update.message.reply_text("⛔ Unauthorized")
return
if not context.args:
help_text = """
💡 **AI Assistant Commands:**
**Usage:** `/help [your request]`
**Examples:**
• `/help write product review for coffee maker 100 words`
• `/help translate to hindi: Hello how are you`
• `/help format this data: John,25,NYC Mary,30,LA`
• `/help summarize: [paste long text]`
**Or just ask:**
• `/help how to write good reviews`
• `/help tips for data entry tasks`
"""
await update.message.reply_text(help_text, parse_mode='Markdown')
return
# Get user request
user_request = ' '.join(context.args)
# Send processing message
msg = await update.message.reply_text("🤖 AI processing your request...")
# Call Groq AI
prompt = f"You are a helpful freelance task assistant. Help with this request
concisely and practically:\n\n{user_request}"
ai_response = call_groq_ai(prompt, max_tokens=800)
# Send response
await msg.edit_text(f"💡 **AI Assistant:**\n\n{ai_response}",
parse_mode='Markdown')
# Add action buttons
keyboard = [
[
InlineKeyboardButton("📋 Copy", callback_data="copy_response"), InlineKeyboardButton("🔄
Regenerate",
callback_data=f"regen_{user_request[:50]}")
]
]
await context.bot.send_message(
chat_id=update.effective_chat.id,
text="**Actions:**",
reply_markup=InlineKeyboardMarkup(keyboard),
parse_mode='Markdown'
)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id if not is_authorized(user_id):
await update.message.reply_text("⛔ Unauthorized")
return
# Get or initialize user stats
if user_id not in user_stats:
user_stats[user_id] = {
"tasks_completed": 0,
"total_earnings": 0.0,
"total_time": 0,
"today_tasks": 0,
"today_earnings": 0.0
}
stats_data = user_stats[user_id]
stats_text = f"""
📊 **Your Statistics**
**Today:**
✅ Tasks: {stats_data['today_tasks']}
💰 Earnings: ${stats_data['today_earnings']:.2f}
📈 Avg: ${(stats_data['today_earnings'] / stats_data['today_tasks'] if
stats_data['today_tasks'] > 0 else 0):.2f}/task
**All Time:**
✅ Total Tasks: {stats_data['tasks_completed']}
💰 Total Earned: ${stats_data['total_earnings']:.2f}
⏱️ Time Spent: {stats_data['total_time']} hou 🎯 **Keep it up!
"""
keyboard = [
[
InlineKeyboardButton("📅 Weekly", callback_data="stats_weekly"),
InlineKeyboardButton("📆 Monthly", callback_data="stats_monthly")
],
[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
]
await update.message.reply_text(
stats_text,
reply_markup=InlineKeyboardMarkup(keyboard),
parse_mode='Markdown'
)
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
if not is_authorized(user_id):
await update.message.reply_text("⛔ Unauthorized")
return
settings_text = """
⚙️ **Bot Settin **Current Configuration:**
✅ AI Mode: Groq (Free)
✅ Language: English + Hindi
✅ Notifications: Enabled
✅ Auto-save: Enabled
**Your User ID:** `{user_id}`
Use this ID in .env file for authorization.
"""
keyboard = [
[
InlineKeyboardButton("🔔 Notifications", callback_data="toggle_notif"),
InlineKeyboardButton("🌐 Language", callback_data="change_lang")
],
[InlineKeyboardButton("📖 Help", callback_data="show_help")] ]
await update.message.reply_text(
settings_text.format(user_id=user_id),
reply_markup=InlineKeyboardMarkup(keyboard),
parse_mode='Markdown'
)
# Callback handlers
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
user_id = query.from_user.id
if not is_authorized(user_id):
await query.edit_message_text("⛔ Unauthorized")
return
data = query.data
if data.startswith("help_"):
task_id = int(data.split("_")[1])
task = next((t for t in DEMO_TASKS if t['id'] == task_id), None)
if task:
await query.edit_message_text("🤖 AI generating help for this task...")
prompt = f"Generate a helpful draft for this freelance task:\nTitle:
{task['title']}\nDescription: {task['desc']}\nProvide practical, ready-to-use
content."
ai_response = call_groq_ai(prompt, max_tokens=600)
await query.edit_message_text(
f"💡 **AI Help for: {task['title']}**\n\n{ai_response}",
parse_mode='Markdown'
)
elif data.startswith("done_"):
task_id = int(data.split("_")[1])
task = next((t for t in DEMO_TASKS if t['id'] == task_id), None) if task: # Update stats
if user_id not in user_stats:
user_stats[user_id] = {
"tasks_completed": 0,
"total_earnings": 0.0,
"total_time": 0,
"today_tasks": 0,
"today_earnings": 0.0
}
pay_amount = float(task['pay'].replace('$', ''))
time_min = int(task['time'].split()[0])
user_stats[user_id]["tasks_completed"] += 1
user_stats[user_id]["total_earnings"] += pay_amount
user_stats[user_id]["total_time"] += time_min / 60
user_stats[user_id]["today_tasks"] += 1
user_stats[user_id]["today_earnings"] += pay_amount
await query.edit_message_text(
f"🎉 **Task Marked Complete!**\n\n"
f"💰 Earned: {task['pay']}\n"
f"⏱️ Time: {task['time']}\
f"📊 Total Today: ${user_stats[user_id]['today_earnings']:.2f}",
parse_mode='Markdown'
)
elif data.startswith("save_"):
await query.edit_message_text("⭐ Task saved for later!")
elif data == "refresh_tasks":
await query.edit_message_text("🔄 Refreshing tasks...")
# Trigger find_tasks again
await find_tasks(update, context)
elif data == "refresh_stats":
await query.edit_message_text("🔄 Refreshing stats...")
await stats(update, context)
# Message handler for direct AI chat
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
if not is_authorized(user_id): return
text = update.message.text
# Check if it's a question or request
if any(word in text.lower() for word in ['how', 'what', 'write', 'help',
'translate', 'create', '?']):
msg = await update.message.reply_text("🤖 Thinking...")
prompt = f"You are a helpful freelance assistant. Answer this
concisely:\n\n{text}"
ai_response = call_groq_ai(prompt) await msg.edit_text(f"💡 {ai_response}")
# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
logger.error(f"Update {update} caused error {context.error}")
if update and update.effective_message:
await update.effective_message.reply_text(
"❌ An error occurred. Please try again or contact support."
)
# Main function
def main():
# Validation
if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
print("❌ ERROR: Please set BOT_TOKEN in .env file!")
print("Get token from @BotFather on Telegram")
return
if GROQ_API_KEY == 'YOUR_GROQ_KEY_HERE':
print("⚠️ WARNING: Groq API key not set. AI features will be limite
print("Get free key from https://console.groq.com")
if ADMIN_USER_ID == 0:
print("⚠️ WARNING: ADMIN_USER_ID not set. Anyone can use bo
print("Use /settings command to get your user ID")
# Create application
application = Application.builder().token(BOT_TOKEN).build()
# Add handlers application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("findtasks", find_tasks))
application.add_handler(CommandHandler("help", ai_help))
application.add_handler(CommandHandler("stats", stats))
application.add_handler(CommandHandler("settings", settings))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
handle_message))
application.add_error_handler(error_handler)
# Start bot
print("🚀 Bot starting...")
print(f"✅ Telegram Bot API: Connected")
print(f"✅ Groq AI: {'Enabled' if GROQ_API_KEY != 'YOUR_GROQ_KEY_HERE' else
'Disabled'}")
print(f"✅ Security: {'Private mode' if ADMIN_USER_ID != 0 else 'Public (set
ADMIN_USER_ID!)'}")
application.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__ == '__main__':
main()