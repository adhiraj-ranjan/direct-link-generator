from telegram.ext import filters, MessageHandler, CommandHandler, Application
from convert import identify_service_convert, extract_first_link
import requests
from os import environ

TOKEN = environ['TOKEN'] # Bot token here

async def start(update, context):
    await update.message.reply_text("🔥 Supported Sites\n - GoogleDrive\n - OneDrive\n - MediaFire")

async def handle_url(update, context):
    req_url = extract_first_link(update.message.text)
    if not req_url:
        await update.message.reply_text("URL not found!")
        return

    direct_url = identify_service_convert(req_url)

    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={update.message.chat.id}&text=`{direct_url}`&parse_mode=MarkDown")

# Log errors
# async def error(update, context):
#     print(context.error)
#     if update:
#         await update.message.reply_text(str(context.error))



# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT, handle_url))
    
    # Log all errors
    # app.add_error_handler(error)

    app.run_polling()
