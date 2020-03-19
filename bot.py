import os
import time
import threading
from telegram.ext import Updater, CommandHandler

from monitor import get_nav_element, explore_nav, pretty_print

TOKEN = os.environ["COVID_LONDON_TOKEN"]
monitor_thread = None
INTERVAL = 3600


class MonitorThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.running = False
        self.updater = None

    def run(self):
        self.running = True
        while True:
            if not self.running:
                break

            nav = get_nav_element()
            if nav is None:
                msg = "Resource not found on web page."
            else:
                res = explore_nav(nav)
                msg = pretty_print(res)

                if not msg:
                    msg = "No results found."

            self.updater.message.reply_text(msg)
            time.sleep(INTERVAL)

    def stop(self):
        self.running = False


def get_one(update, context):
    nav = get_nav_element()
    if nav is None:
        msg = "Resource not found on web page."
    else:
        res = explore_nav(nav)
        msg = pretty_print(res)

        if not msg:
            msg = "No results found."

    update.message.reply_text(msg)


def start(update, context):
    global monitor_thread
    if monitor_thread is not None and monitor_thread.running:
        return
    monitor_thread = MonitorThread(0)
    monitor_thread.updater = update
    monitor_thread.start()


def stop(update, context):
    global monitor_thread
    if monitor_thread is not None and monitor_thread.running:
        monitor_thread.stop()
    monitor_thread = None


def set_interval(update, context):
    global monitor_thread, INTERVAL
    args = context.args
    if len(args) != 1:
        update.message.reply_text("One argument required.")
        return
    try:
        new_interval = int(args[0])
        if new_interval <= 0:
            update.message.reply_text("The new interval must be a number higher than 0.")

        run = False
        if monitor_thread is not None and monitor_thread.running:
            monitor_thread.stop()
            run = True

        INTERVAL = new_interval * 60
        msg = "Interval updated to {}".format(new_interval)
        update.message.reply_text(msg)
        monitor_thread = MonitorThread(0)
        if run:
            monitor_thread.updater = update
            monitor_thread.start()
    except ValueError:
        update.message.reply_text("Impossible to convert argument to integer.")


def helper(update, context):
    msg = """Commands list:
    
/start - start to receive messages
/stop - stop to receive messages
/set_interval - update the interval between the messages (minutes)
/get_one - get just one message now
/help - this helper"""

    update.message.reply_text(msg)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("set_interval", set_interval))
    dp.add_handler(CommandHandler("get_one", get_one))
    dp.add_handler(CommandHandler("help", helper))

    # Start the Bot
    updater.start_polling()


if __name__ == "__main__":
    try:
        main()
        print("Bot is running...")
    except:
        monitor_thread.exc_rate_monitor.close()
