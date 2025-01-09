import math
import os
from json_funcs import modify_streamer_settings, modify_streamer_values
from ignore_these_words import IGNORE_WORDS
from twitchio.ext import commands  # type: ignore
import random
from syllafunc import syllables_split, syllables_to_sentence
from dotenv import load_dotenv
import json
import logging

# Create a folder for logs if it doesn't exist
if not os.path.exists("streamer_logs"):
    os.makedirs("streamer_logs")

# Function to set up a logger for a specific channel, saving logs in streamer_logs folder


def setup_channel_logger(channel_name: str):
    # Log file in streamer_logs folder
    log_filename = os.path.join("streamer_logs", f"{channel_name}.log")
    logger = logging.getLogger(channel_name)

    # Check if the logger already has handlers to avoid duplicates
    if not logger.hasHandlers():
        # You can adjust the level (e.g., INFO, WARNING, etc.)
        logger.setLevel(logging.DEBUG)

        # Create a file handler to write to the channel's log file
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # Create a log formatter and attach it to the file handler
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

    return logger


# This function will return a logger for the specific channel


def get_logger_for_channel(channel_name: str):
    return setup_channel_logger(channel_name)


load_dotenv()
access_token = os.environ.get('TMI_TOKEN')

# json containing settings for each streamer
json_data_path = "streamer_settings.json"
BUTT_RATE_PER_SENTENCE = 10
UPPER_LIMIT_BUTTRATE = 1000
LOWER_LIMIT_BUTTRATE = 10


class Bot(commands.Bot):

    def __init__(self, data: dict):
        super().__init__(token=access_token, prefix='!', initial_channels=list(data.keys()))
        self.channel_settings: dict = data

    async def event_ready(self):
        # Get logger for the bot's channel
        logger = get_logger_for_channel(self.nick)
        logger.info(f'Logged in as | {self.nick}')
        logger.info(f'User id is | {self.user_id}')

        if self.nick not in self.channel_settings:
            logger.info(
                f'Adding bot {self.nick} to settings with default values...')
            self.channel_settings[self.nick] = {"rate": 30, "word": "BUTT"}

            modify_streamer_settings(json_data_path, "add", {
                                     self.nick: self.channel_settings[self.nick]})

        logger.info(
            f'channels connected to: {list(self.channel_settings.keys())}')

    async def event_command_error(self, ctx, error: Exception) -> None:
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f'Wait a couple of seconds before sending something else, {ctx.author.name}!')
            logger.warning(
                f'Command on cooldown: {ctx.command.name} from {ctx.author.name}')

    async def event_message(self, message):
        if message.echo:
            return

        # Get logger for the current channel
        logger = get_logger_for_channel(message.channel.name)

        channel_name = message.channel.name
        settings = self.channel_settings.get(channel_name)
        random_int = random.randint(1, settings["rate"])

        if settings and random_int == 1:
            syllable_lists = syllables_split(message.content)
            butt_num = math.ceil(len(syllable_lists) / BUTT_RATE_PER_SENTENCE)

            for num in range(butt_num):
                random_word = random.randint(0, len(syllable_lists) - 1)
                attempts = 0
                while len(syllable_lists[random_word]) <= 1 and syllable_lists[random_word][0].lower() in IGNORE_WORDS and attempts < 10:
                    random_word = random.randint(0, len(syllable_lists) - 1)
                    attempts += 1
                    if attempts >= 9:
                        # should rarely ever see this in the logs
                        logger.warning(
                            'Could not find a word to replace, skipping message...')
                        return
                logger.info(
                    f'replacing the word {syllable_lists[random_word]}')
                random_syllable = random.randint(
                    0, len(syllable_lists[random_word]) - 1)
                syllable_lists[random_word][random_syllable] = settings["word"]
                logger.info(
                    f'replacing the syllable {syllable_lists[random_word][random_syllable]}')
            new_message = syllables_to_sentence(syllable_lists)
            logger.info(f'{message.author.name}: {new_message}')
            await message.channel.send(f'{new_message}')

        await self.handle_commands(message)

    @ commands.command()
    @ commands.cooldown(3, 45, commands.Bucket.user)
    async def hello(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        await ctx.channel.send(f'hiii {ctx.author.name}!')
        logger.info(f"Hello command invoked by {ctx.author.name}")

    @ commands.command()
    async def join(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        channel_name = ctx.author.name

        if channel_name not in self.channel_settings:
            self.channel_settings[channel_name] = {"rate": 30, "word": "BUTT"}
            modify_streamer_settings(json_data_path, "add", {
                                     channel_name: self.channel_settings.get(channel_name)})

            await ctx.send(f'Joining {channel_name}\'s channel')
            await self.join_channels([channel_name])
            logger.info(f"Joining channel: {channel_name}")
        else:
            await ctx.send(f'Already in {channel_name}\'s channel.')

    @ commands.command()
    async def leave(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        channel_name = ctx.author.name

        if channel_name != ctx.channel.name:
            await ctx.send(f'Please use the !leave command in your own channel.')
            logger.warning(
                f'Non-host trying to remove me from the channel {channel_name}.')
            return

        if channel_name in self.channel_settings:
            modify_streamer_settings(json_data_path, "rm", {
                                     channel_name: self.channel_settings[channel_name]})
            del self.channel_settings[channel_name]

            await ctx.send(f'Leaving {channel_name}\'s channel.')
            await self.part_channels([channel_name])
            logger.info(f"Leaving channel: {channel_name}")
        else:
            await ctx.send(f'The bot is not currently in {channel_name}\'s channel.')

    @ commands.command()
    async def buttrate(self, ctx: commands.Context, new_rate: str = None):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        message_user_name = ctx.author.name
        channel_name = ctx.channel.name
        settings = self.channel_settings.setdefault(
            message_user_name, {"rate": 30, "word": "BUTT"})

        if new_rate is None:
            if message_user_name != channel_name:
                logger.info(
                    f'{message_user_name} tried to check the rate of {channel_name}')
                return
            await ctx.channel.send(f'The current rate is {settings["rate"]}.')
            logger.info(f"Checked rate: {settings['rate']}")
        else:
            if message_user_name != channel_name:
                logger.warning(
                    f'{message_user_name} tried to change the rate of {channel_name}')
                return
            try:
                new_rate = int(new_rate)
                if LOWER_LIMIT_BUTTRATE <= new_rate <= UPPER_LIMIT_BUTTRATE:
                    settings["rate"] = new_rate
                    modify_streamer_values(
                        json_data_path, message_user_name, "rate", new_rate)
                    await ctx.channel.send(f'Rate set to {new_rate}.')
                    logger.info(
                        f"Rate set to {new_rate} for channel: {channel_name}")
                else:
                    await ctx.channel.send(f'{new_rate} is not a valid rate. Please choose a number between 10 and 1000.')
            except ValueError:
                await ctx.channel.send(f'"{new_rate}" is not a valid number. Please enter a valid number between 10 and 1000.')
                logger.warning(f"Invalid rate input: {new_rate}")

    @ commands.command()
    async def buttword(self, ctx: commands.Context, new_word: str = None):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        channel_name = ctx.channel.name
        settings = self.channel_settings.setdefault(
            channel_name, {"rate": 30, "word": "BUTT"})

        if new_word is None:
            await ctx.channel.send(f'The current word for this channel is {settings["word"]}.')
        else:
            if channel_name != ctx.author.name:
                await ctx.channel.send(f'You can only change the word for your own channel.')
                logger.warning(
                    f"{ctx.author.name} tried to change the word for {channel_name}")
                return
            settings["word"] = new_word
            modify_streamer_values(
                json_data_path, channel_name, "word", new_word)
            await ctx.channel.send(f'Word for this channel changed to {settings["word"]}.')
            logger.info(
                f"Word changed to {settings['word']} for channel: {channel_name}")


def main():
    if os.path.exists(json_data_path):
        with open(json_data_path, "r") as json_file:
            settings = json.load(json_file)
    else:
        settings = {}

    # You can set up a general logger for the bot if needed
    logger = get_logger_for_channel("bot")
    logger.info(f'current settings: {settings}')
    logger.info(f'successfully loaded settings...')
    bot = Bot(settings)
    bot.run()


if __name__ == "__main__":
    main()
