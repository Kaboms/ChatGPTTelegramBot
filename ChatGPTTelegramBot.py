import argparse
import openai
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, MessageHandler, ContextTypes, CommandHandler

def get_chat_GPT_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            temperature=0.5,
        )
        return response["choices"][0]["text"]
    except openai.error.AuthenticationError:
        return "Your api key is invalid"
    except Exception as ex:
        print(ex)
        return "ERROR: Failed to get response from Chat GPT"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello. Use /key command to register your Chat GPT API Key")

async def request_chat_GPT(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = context.user_data.get('chat_gpt_token', None)
    if api_key is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Use /key command to register your Chat GPT API Key')
    else:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=get_chat_GPT_response(update.message.text))

async def key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = context.user_data.get('chat_gpt_token', None)
    if len(context.args) == 0:
        if api_key is None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Get your key from https://beta.openai.com/account/api-keys and send me:\n/key you_api_key")
            return
    else:
        api_key = context.args[0]
        openai.api_key = api_key
        context.user_data['chat_gpt_token'] = api_key
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Chat GPT api key is: {api_key}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-botToken', dest='botToken', default='', type=str, required=True, help='Telegram bot token')
    args = parser.parse_args()

    application = ApplicationBuilder().token(args.botToken).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('key', key))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), request_chat_GPT))

    application.run_polling()