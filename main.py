from telegram import Update
from telegram.ext import ApplicationBuilder
from os import getenv
from telegram import Update
from telegram.ext import (CommandHandler,
                          ConversationHandler, MessageHandler, filters, ContextTypes)
from logging import warning
from pydantic import BaseModel, Field, validator

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    raise ValueError('TELEGRAM_TOKEN is not set')

# class ProjectIdeas(BaseModel):
#     project_ideas: list[str] = Field(description="List of project ideas.")
    
class Job(BaseModel):
    title: str

    @validator('title')
    def is_valid_job(cls, value: str):
        valid_jobs = ['data scientist', 'machine learning engineer', 'data analyst', 'data engineer', 'statistician', 'ml researcher', 'data architect', 'data mining engineer', 'applied ml scientist', 'data science manager', 'ml ops engineer', 'data science intern', 'research data scientist', 'senior data scientist', 'lead data scientist', 'principal data scientist', 'chief data scientist', 'business intelligence analyst']
        if value.lower() not in valid_jobs:
            raise ValueError('Oops! Only Data Science and Analytics jobs are allowed for now! You can /start over!')
        return value


async def hello(update: Update, context) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. I am The Data Alchemist. Click on /start to get started!')


async def start(update: Update, context):
    """Welcome the user and ask for their job title."""
    await update.message.reply_text("Hi, I am The Data Alchemist, your AI assistant.\nI am here to help you get started with your career growth.\nPlease tell me your job title.")
    return 1


async def job_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the job title and ask for the job level."""
    try:
        job = Job(title=update.message.text)
        context.user_data['job_title'] = job.title
        await update.message.reply_text(f"Got it, your job title is {context.user_data['job_title']}. What is your job level?")
        return 2
    except ValueError as e:
        error_message = e.errors()[0]['msg']
        await update.message.reply_text(error_message)
        return ConversationHandler.END

async def job_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the job level and ask for the industry."""
    context.user_data['job_level'] = update.message.text
    await update.message.reply_text(
        "Thanks. Finally, what industry are you looking to work in?")
    return 3


async def industry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the industry and display the gathered information."""
    context.user_data['industry'] = update.message.text
    await update.message.reply_text(
        f"Here's the information I gathered: \nJob Title: {context.user_data['job_title'].title()}\nJob Level: {context.user_data['job_level'].title()}\nIndustry: {context.user_data['industry'].title()}"
    )
    return ConversationHandler.END

async def cancel(update: Update, context):
    """Cancel the conversation."""
    await update.message.reply_text('Bye! I canceled the conversation.')
    return ConversationHandler.END


async def error(update: Update, context):
    """Log Errors caused by Updates."""
    warning('Update "%s" caused error "%s"', update, context.error)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        1: [MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=job_title)],
        2: [MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=job_level)],
        3: [MessageHandler(filters=filters.TEXT & (~filters.COMMAND), callback=industry)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    , per_user=True
)
bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

bot.add_handler(conversation_handler)
bot.error_handlers(error)

bot.run_polling()