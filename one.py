from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext

FIRST, SECOND, DESCRIPTION = range(3)

support_requests = []

first_level_options = {
    '1': "Login Issues",
    '2': "Payment Problems",
    '3': "Technical Support"
}

second_level_options = {
    '1': ["Forgot Password", "Account Locked", "Two-Factor Authentication"],
    '2': ["Failed Transaction", "Refund Request", "Invoice Issues"],
    '3': ["Bug Report", "Feature Request", "Performance Issues"]
}

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Login Issues", callback_data='1')],
        [InlineKeyboardButton("Payment Problems", callback_data='2')],
        [InlineKeyboardButton("Technical Support", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! What is your problem?', reply_markup=reply_markup)
    return FIRST

async def first_stage(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()  # Yanıtı hemen gönder
    context.user_data['first_choice'] = query.data
    keyboard = [
        [InlineKeyboardButton(option, callback_data=str(index + 1)) for index, option in enumerate(second_level_options[query.data])]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Please select the specific issue:", reply_markup=reply_markup)
    return SECOND

async def second_stage(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()  # Yanıtı hemen gönder
    first_choice = context.user_data['first_choice']
    second_choice = query.data
    context.user_data['second_choice'] = second_choice
    issue = second_level_options[first_choice][int(second_choice) - 1]
    await query.edit_message_text(text="Please describe your issue in your own words:")
    return DESCRIPTION

async def description(update: Update, context: CallbackContext) -> int:
    description = update.message.text
    first_choice = context.user_data['first_choice']
    second_choice = context.user_data['second_choice']
    issue = second_level_options[first_choice][int(second_choice) - 1]
    user_id = update.effective_user.id
    support_requests.append((user_id, issue, description))
    await update.message.reply_text(f"We understand your issue: {issue}. A human support agent will contact you shortly.")
    admin_id = 1597091130
    await context.bot.send_message(admin_id, f"New support request from user {user_id}: {issue}\nDescription: {description}")
    return ConversationHandler.END

async def view_requests(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 1597091130:
        if support_requests:
            message = "Support Requests:\n"
            for user_id, issue, description in support_requests:
                message += f"User {user_id}: {issue}\nDescription: {description}\n\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("No support requests at the moment.")
    else:
        await update.message.reply_text("You are not authorized to view support requests.")

async def reply(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 1597091130:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /reply <user_id> <message>")
            return
        user_id = int(args[0])
        message = ' '.join(args[1:])
        await context.bot.send_message(user_id, f"Support response: {message}")
        await update.message.reply_text(f"Response sent to user {user_id}.")
    else:
        await update.message.reply_text("You are not authorized to reply to support requests.")

def main() -> None:
    application = Application.builder().token("7455577173:AAF3IaxGnqdCYc8zJzazl-rqsm_bZnn3ugI").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(first_stage)],
            SECOND: [CallbackQueryHandler(second_stage)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        },
        fallbacks=[],
        per_chat=False,
        per_user=True,
        per_message=False,
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('view_requests', view_requests))
    application.add_handler(CommandHandler('reply', reply))
    application.run_polling()

if __name__ == '__main__':
    main()
