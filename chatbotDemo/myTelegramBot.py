import logging
import os
import chatbotController as cc
import constants as con
import dto.user as user
import service.userDataService as us
from time import sleep
from random import random
from telegram.constants import ChatAction
from telegram import *
from telegram.ext import *
from dotenv import load_dotenv, find_dotenv
from functools import wraps
import service.foodHistoryService as foodHistory


load_dotenv(find_dotenv())
token = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


userData = ''
userMessage = ''

#chatbot states
INTERACTION = range(1)

def update_context(context: ContextTypes.DEFAULT_TYPE, response):
        context.user_data['action'] = response.action
        context.user_data['memory'] = response.memory
        context.user_data['info'] = response.info
        return context

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
    telegramUser = update.message.from_user
    context.user_data['info'] = ''
    context.user_data['userData'] =  us.getUserData(telegramUser['id'])

    #if the user data is empty the start a "get data", conversation
    if(context.user_data['userData'] == None):
        context.user_data['userData'] = user.User(telegramUser['username'],telegramUser['id'],None,None,None,None,None,None)
        response = cc.answer_question(context.user_data['userData'],con.USER_FIRST_MEETING_PHRASE,con.TASK_0_HOOK,"",None)
        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        context = update_context(context,response)
    else:
        response = cc.answer_question(context.user_data['userData'],con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"",None)
        foodHistory.clean_temporary_declined_suggestions(context.user_data['userData'].id)
        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        context = update_context(context,response)
    return INTERACTION

@send_action(ChatAction.TYPING)
async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manage the conversation loop between the user and the chatbot."""
    userMessage = update.message.text
    response = cc.aswer_router(context.user_data['userData'],userMessage,context.user_data['action'],context.user_data['memory'],context.user_data['info'])
    await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
    context = update_context(context,response)
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

