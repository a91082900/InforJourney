from OutputPTB import OutputPTB as Output
from secret import TOKEN
from typing import Dict
from telegram.ext import (Filters, Updater, Updater, CommandHandler, 
    CallbackQueryHandler, MessageHandler)
from Game import Game, stat_ids
from MapPainter import MapPainter

games: Dict [int, Game] = {}
updater = Updater(TOKEN)
dispatcher = updater.dispatcher
print(f"@{updater.bot.getMe().username}")

def pre_process(update, context):
    global gid, game, uid
    gid = update.message.chat_id
    if gid not in games:
        out = Output(context.bot, gid, gid)
        games[gid] = Game(gid, out)
    game = games[gid]
    uid = update.message.from_user.id

def add_command(name=None, group=1):
    def wrapper(func):
        nonlocal name
        if not name:
            name = func.__name__
        dispatcher.add_handler(CommandHandler(name, func), group)
        return func
    return wrapper

@add_command("map")
def show_map(update, context):
    game.on_draw_map()

@add_command()
def start(update, context):
    game.on_start()

@add_command()
def jizz(update, context):
    try:
        game.on_jizz(uid, int(context.args[0]))
    except:
        game.on_jizz(uid)

# @add_command("map")
# def show_map(update, context):
#     game.on_map()

@add_command()
def pos(update, context):
    game.on_pos(uid)

@add_command()
def upgrade(update, context):
    args = context.args
    try:
        game.on_upgrade(uid, args[0], 1 if len(args) < 2 else args[1])
    except Exception as e:
        print("ERROR:", e)
        game.out.send_wrong_argument()

@add_command()
def buy(update, context):
    args = context.args
    try:
        game.on_buy(uid, int(args[0]))
    except Exception as e:
        print("ERROR:", e)
        game.out.send_wrong_argument()

@add_command()
def mystat(update, context):
    game.on_mystat(uid)

@add_command()
def end(update, context):
    game.on_end(uid)

@add_command("help")
def show_help(update, context):
    game.on_help()

@add_command()
def showpotion(update, context):
    game.on_show_potion(uid)

@add_command()
def drink(update, context):
    args = context.args
    try:
        game.on_drink(uid, int(args[0]))
    except:
        game.out.send_wrong_argument()

@add_command()
def join(update, context):
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    # if there is no username, this column will be None
    print(game.out.send_welcome)
    game.on_join(uid, name, username)

@add_command()
def change(update, context):
    game.on_change(uid)

@add_command()
def retire(update, context):
    game.on_retire(uid)

@add_command()
def showstat(update, context):
    game.on_show_stat(uid)

def handle_callback(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    from_id = query.from_user.id
    query_data = query.data.split()
    gid = int(query_data[-1])
    del query_data[-1]
    identifier = (chat_id, query.message.message_id)
    if gid in games:
        games[gid].passage(query_data, from_id, identifier)
    # game = None
    # if chat_id in games:
    #     game = games[chat_id] 
    # elif chat_id in stat_ids:
    #     game = stat_ids[chat_id] 
    # else:
    #     print("Game did not start")
    # if game:
    #     game.passage(query_data.split(), from_id, identifier)
    query.answer()


dispatcher.add_handler(MessageHandler(Filters.command, pre_process), 0)
dispatcher.add_handler(CallbackQueryHandler(handle_callback))

updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()