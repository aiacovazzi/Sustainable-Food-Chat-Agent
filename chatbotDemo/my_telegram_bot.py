import logging
import os
import chatbotController as cc
import constants as con
import dto.responseClass as rc
import service.userDataService as us
from time import sleep
from random import random
from telegram.constants import ChatAction
from telegram import *
from telegram.ext import *
from dotenv import load_dotenv, find_dotenv
from functools import wraps

load_dotenv(find_dotenv())
token = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


userData = ''
userMessage = ''

#chatbot states
INTERACTION = range(1)

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation."""
    context.user_data['userData'] =  us.getUserData(update.message.from_user['id'])
    #if the user data is empty the start a "get data", conversation
    response = cc.answerQuestion(context.user_data['userData'],"Hi, who are you?",con.TASK_1_HOOK,"")
    await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
    context.user_data['action'] = response.action
    return INTERACTION

@send_action(ChatAction.TYPING)
async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manage the conversation loop between the user and the chatbot."""
    userMessage = update.message.text
    sleep(random() * 2 + 3.)
    response = cc.aswerRouter(context.user_data['userData'],userMessage,context.user_data['action'])
    await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
    context.user_data['action'] = response.action
    return None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INTERACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, interaction)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    application.run_polling()

if __name__ == '__main__':
    main()