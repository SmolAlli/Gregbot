import math
import os
import random
import json
from typing import Dict
from dotenv import load_dotenv
from twitchio.ext import commands  # type: ignore
from json_funcs import modify_streamer_settings, modify_streamer_values, add_ignore_list, remove_ignore_list, open_file
from ignore_these_words import IGNORE_WORDS
from logging_funcs import get_logger_for_channel
from other_bot_funcs import in_bot_channel
from plural_funcs import get_buttword_plural,  get_syllables_no_punctuation
from regex_funcs import is_punctuation
from syllable_funcs import syllables_split, syllables_to_sentence

# Create a folder for logs if it doesn't exist
if not os.path.exists("streamer_logs"):
    os.makedirs("streamer_logs")

# Load up the .env files
load_dotenv()
bot_access_token = os.environ.get('TMI_TOKEN')
bot_nickname = os.environ.get('BOT_NICKNAME').lower()
bot_prefix = os.environ.get('BOT_PREFIX')

# JSON containing settings for each streamer
JSON_DATA_PATH = "streamer_settings.json"
# JSON containing list of ignored users
IGNORED_LIST_PATH = "ignored.json"

# butts per __ words in a message
BUTT_REPLACEMENT_PER_SENTENCE = 10
# highest possible buttrate
UPPER_LIMIT_BUTTRATE = 1000
# lowest possible buttrate
LOWER_LIMIT_BUTTRATE = 10
# attempts to find a replacement in a message before fail
MAX_WORD_ATTEMPTS = 10
# default streamer settings
DEFAULT_BUTT_INFO = {"rate": 30, "word": "butt", "random_words_enabled": False, "random_words_list": []}


class Bot(commands.Bot):
    def __init__(self, data: dict):
        super().__init__(token=bot_access_token, prefix=bot_prefix,
                         initial_channels=list(data.keys()))
        self.channel_settings: dict = data
        self.missed_messages: Dict[str, int] = {}

    async def event_ready(self):
        # Get logger for the bot's channel
        logger = get_logger_for_channel(self.nick)
        logger.info(f'Logged in as | {self.nick}')
        logger.info(f'User id is | {self.user_id}')

        if self.nick not in self.channel_settings:
            logger.info(
                f'Adding bot {self.nick} to settings with default values...')
            self.channel_settings[self.nick] = DEFAULT_BUTT_INFO

            modify_streamer_settings(JSON_DATA_PATH, "add", {
                                     self.nick: self.channel_settings[self.nick]})

        logger.info(
            f'channels connected to: {list(self.channel_settings.keys())}')

    async def event_command_error(self, context, error: Exception) -> None:
        # Get logger for the current channel
        logger = get_logger_for_channel(context.channel.name)
        if isinstance(error, commands.CommandOnCooldown):
            await context.channel.send(
                f'Wait a couple of seconds before sending something else, {context.author.name}!')
            logger.warning(
                f'Command on cooldown: {context.command.name} from {context.author.name}')

    def increase_missed_messages(self, name):
        self.missed_messages[name] += 1

    def find_valid_syllable(self, message, syllable_lists):
        # Get logger for the current channel
        logger = get_logger_for_channel(message.channel.name)

        random_word = 0
        for _ in range(10):  # 10 attempts to find a new word
            random_word = random.randint(0, len(syllable_lists) - 1)
            # If an ignored word, find another word
            if "".join(get_syllables_no_punctuation(
                    syllable_lists[random_word])).lower() in IGNORE_WORDS:
                continue

            # Word is fine, continue forward
            break
        else:
            logger.warning(
                'Could not find a word to replace, skipping message...')
            return False

        random_syllable = 0
        for _ in range(5):  # 5 attempts to find a new syllable
            random_syllable = random.randint(
                0, len(syllable_lists[random_word]) - 1)
            # If the syllable is only 1 letter, don't use
            if len(syllable_lists[random_word][random_syllable]) == 1:
                continue

            # If the syllable contains punctuation, don't use
            if is_punctuation(syllable_lists[random_word][random_syllable]):
                continue

            # Syllable is fine, continue forward
            break
        else:
            logger.warning(
                'Could not find a syllable to replace, skipping message...')
            return False

        return [random_word, random_syllable]

    def find_buttwords(self, message):
        # Get logger for the current channel
        channel_name = message.channel.name
        logger = get_logger_for_channel(channel_name)

        settings = self.channel_settings.get(channel_name)

        syllable_lists = syllables_split(message.content)

        # calc the number of replacements in the sentence
        butt_num = math.ceil(
            len(syllable_lists) / BUTT_REPLACEMENT_PER_SENTENCE)

        valid_butts = 0
        for _ in range(butt_num):
            out = self.find_valid_syllable(message, syllable_lists)

            if out is not False:
                random_word = out[0]
                random_syllable = out[1]

                # grab length of the random_words list
                rand_words_len = len(settings["random_words"])

                # decide which streamer word to use:
                # if random_words are enabled, choose from there, otherwise take the single set word
                streamer_word_final = settings["word"] if not settings["random_words_enabled"] else settings["random_words"][random.randint(
                    0, rand_words_len)]

                # Check if the given syllable should be plural
                buttword = get_buttword_plural(
                    streamer_word_final, syllable_lists[random_word], random_syllable)

                # Only log the word replacement once, not as word and syllable separately
                logger.info(
                    f"replaced syllable \'{syllable_lists[random_word][random_syllable]}\' in word \'{syllable_lists[random_word]}\' with \'{buttword}\' " +
                    f"in the message \'{message.content}\' sent by {message.author.name}")

                syllable_lists[random_word][random_syllable] = buttword

                valid_butts += 1

        if valid_butts == 0:
            return False

        return syllable_lists

    async def event_message(self, message):
        channel_name = message.channel.name

        if message.echo:
            return

        print(message.content)
        # Make sure to not butt in the bot's channel
        if not channel_name == bot_nickname:
            # check if missed_messages has the channel name as a key
            if channel_name not in self.missed_messages:
                # add the channel name as a key and set the value to 0
                self.missed_messages[channel_name] = 0

            # Check if the user is ignored
            if message.author.name not in open_file(IGNORED_LIST_PATH, []):
                # grab the channel's settings
                settings = self.channel_settings.get(channel_name)

                # grab the butt rate for the channel
                butt_rate = settings["rate"]

                # calculate the final butt rate for the channel
                # once the missed message count exceeds the butt rate,
                # the bot will have an increased chance of responding
                # ensure final_butt_rate is at least 1 otherwise random.randint will throw an error
                final_butt_rate = max(butt_rate - max(self.missed_messages[channel_name] - butt_rate, 0), 1)

                if settings and random.randint(1, final_butt_rate) == 1:
                    butt_sentence = self.find_buttwords(message)

                    # Make sure that it didn't return false i.e. didn't replace anything
                    if butt_sentence is not False:
                        await message.channel.send(f'{syllables_to_sentence(butt_sentence)}')
                        # set missed messages for channel back to 0
                        self.missed_messages[channel_name] = 0
                else:
                    # increment the missed messages for the channel
                    self.increase_missed_messages(channel_name)

        await self.handle_commands(message)

    @commands.command()
    @commands.cooldown(3, 45, commands.Bucket.user)
    async def hello(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        await ctx.channel.send(f'hiii {ctx.author.name}!')
        logger.info(f"Hello command invoked by {ctx.author.name}")

    @commands.command()
    async def join(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        channel_name = ctx.author.name

        if channel_name not in self.channel_settings:
            self.channel_settings[channel_name] = DEFAULT_BUTT_INFO
            modify_streamer_settings(JSON_DATA_PATH, "add", {
                                     channel_name: self.channel_settings.get(channel_name)})

            await ctx.send(f'Joining {channel_name}\'s channel')
            await self.join_channels([channel_name])
            logger.info(f"Joining channel: {channel_name}")
        else:
            await ctx.send(f'Already in {channel_name}\'s channel.')

    @commands.command()
    async def leave(self, ctx: commands.Context):
        # Do command for the user's channel instead of channel done in if it's the bot's channel
        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)

        # Get logger for the current channel
        logger = get_logger_for_channel(channel_name)

        if not is_in_bot_channel and channel_name != ctx.author.name:
            await ctx.send('Please use the !leave command in your own channel.')
            logger.warning(
                f'Non-host trying to remove me from the channel {channel_name}.')
            return

        if channel_name in self.channel_settings:
            modify_streamer_settings(JSON_DATA_PATH, "rm", {
                                     channel_name: self.channel_settings[channel_name]})
            del self.channel_settings[channel_name]

            await ctx.send(f'Leaving {channel_name}\'s channel.')
            await self.part_channels([channel_name])
            logger.info(f"Leaving channel: {channel_name}")
        else:
            await ctx.send(f'The bot is not currently in {channel_name}\'s channel.')

    @commands.command(name="randomwords")
    async def randomwords(self, ctx: commands.Context):

        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)
        # Get logger for the current channel
        logger = get_logger_for_channel(channel_name)

        print("here")
        # check where the command is being sent and if the bot has already joined the sender's stream
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            print("and here")
            # check if the user has permission to use the command in the streamer's channel
            if channel_name != ctx.author.name:
                ("sometimes here")
                logger.warning(
                    f"{ctx.author.name} tried to check {channel_name}'s random word list.")
                return

            # grab the streamer's settings
            settings = self.channel_settings.setdefault(
                channel_name, DEFAULT_BUTT_INFO)

            print(len(settings["random_words"]))

            if len(settings["random_words"]) == 0:
                await ctx.channel.send(f'Your word list is empty.')
            else:
                await ctx.channel.send(f'Random Word List: {settings["random_words"]}')

    @commands.command(name="removeword")
    async def removeWord(self, ctx: commands.Context, word: str):
        # Get logger for the current channel
        logger = get_logger_for_channel(channel_name)

        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)

        # check where the command is being sent and if the bot has already joined the sender's stream
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            print("here")
            print("word:", word)
            if word is None or word.strip() == "" or word == "\U000e0000":
                await ctx.channel.send('Make sure to include a word: !addword <word>')
            else:

                # check if the user has permission to change the word
                if channel_name != ctx.author.name:
                    await ctx.channel.send('You can only add words for your own channel.')
                    logger.warning(
                        f"{ctx.author.name} tried to add the word \'{word}\' to {channel_name}'s random word list.")
                    return

                # grab the streamer's settings
                settings = self.channel_settings.setdefault(
                    channel_name, DEFAULT_BUTT_INFO)

                print(settings)

                # check if word isn't in the current list
                if word not in settings["random_words"]:
                    await ctx.channel.send(f'\'{word}\' is not in the word list.')
                    logger.info(
                        f'{channel_name} tried to remove \'{word}\' from their word list and was not found. Current word list: {settings["random_words"]}')
                else:
                    print("also here")
                    # remove the word from settings
                    settings["random_words"].remove(word)
                    # modify the streamer_settings.json random_words list
                    modify_streamer_values(JSON_DATA_PATH, channel_name, "random_words", settings["random_words"])
                    await ctx.channel.send(f'Removed word, \'{word}\'.')

                    logger.info(
                        f'{channel_name} removed the word \'{word}\' from their word list successfully. Current word list: {settings["random_words"]}')

    @commands.command(name="addword")
    async def addWord(self, ctx: commands.Context, word: str):
        # Do command for the user's channel instead of channel done in if it's the bot's channel
        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)
        print("word added:", word)
        # Get logger for the current channel
        logger = get_logger_for_channel(channel_name)

        # check where the command is being sent and if the bot has already joined the sender's stream
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            if word is None or word.strip() == "" or word == "\U000e0000":
                await ctx.channel.send('Make sure to include a word: !addword <word>')
            else:

                # check if the user has permission to change the word
                if channel_name != ctx.author.name:
                    await ctx.channel.send('You can only add words for your own channel.')
                    logger.warning(
                        f"{ctx.author.name} tried to add the word \'{word}\' to {channel_name}'s random word list.")
                    return

                settings = self.channel_settings.setdefault(
                    channel_name, DEFAULT_BUTT_INFO)

                # check if word isn't in the current list
                if word not in settings["random_words"]:
                    # add it to the local list
                    settings["random_words"].append(word)
                    # modify the streamer_settings.json random_words list
                    modify_streamer_values(JSON_DATA_PATH, channel_name, "random_words", settings["random_words"])
                    await ctx.channel.send(f'Added word, \'{word}\'.')
                    logger.info(
                        f'{ctx.message.author} added the word \'{word}\' to their random word list. Current word list: {settings["random_words"]}')

                else:
                    await ctx.channel.send(f'\'{word}\' is already in the list.')
                    logger.info(
                        f'{ctx.message.author} tried to add the word \'{word}\' to their random word list. Current word list: {settings["random_words"]}')

    @commands.command(name="togglerandomwords")
    async def toggleRandomWords(self, ctx: commands.Context):
        # Do command for the user's channel instead of channel done in if it's the bot's channel
        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)

        # If the user is in the bot's channel and checking for their own but has not joined the channel,
        # let the user know of that instead
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            # Get logger for the current channel
            logger = get_logger_for_channel(channel_name)
            # check if the user has permission to change the word
            if channel_name != ctx.author.name:
                await ctx.channel.send('You can only enable/disable random words for your own channel.')
                logger.warning(
                    f"{ctx.author.name} tried to enable/disable random words for {channel_name}")
                return

            settings = self.channel_settings.setdefault(
                channel_name, DEFAULT_BUTT_INFO)

            # enable if disabled
            if not settings["random_words_enabled"]:
                settings["random_words_enabled"] = True
                modify_streamer_values(JSON_DATA_PATH, channel_name, "random_words_enabled", True)
                await ctx.channel.send(f'You have enabled random words{" for @" + channel_name if is_in_bot_channel else ""}. Add words using !addword <word> OR remove words using !removeword <word>.')
            # disable if enabled
            else:
                settings["random_words_enabled"] = False
                modify_streamer_values(JSON_DATA_PATH, channel_name, "random_words_enabled", False)
                await ctx.channel.send(f'You have disabled random words{" for " + channel_name if is_in_bot_channel else ""}.')

            logger.info(
                f'Random words are now {"enabled" if settings["random_words_enabled"] else 'disabled'} for {channel_name}.')

    @commands.command(name="buttrate", aliases=["rate", "setrate"])
    async def buttrate(self, ctx: commands.Context, new_rate: int = None):
        # Do command for the user's channel instead of channel done in if it's the bot's channel
        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)

        # If the user is in the bot's channel and checking for their own but has not joined the channel,
        # let the user know of that instead
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            # Get logger for the current channel
            logger = get_logger_for_channel(channel_name)

            settings = self.channel_settings.setdefault(
                channel_name, DEFAULT_BUTT_INFO)

            if new_rate is None:
                await ctx.channel.send(f'The current rate for the channel {channel_name} is 1/{settings["rate"]}.')
                logger.info(f"Checked rate: {settings['rate']}")
            else:
                if ctx.author.name != channel_name:
                    logger.warning(
                        f'{ctx.author.name} tried to change the rate of {channel_name}')
                    return
                if LOWER_LIMIT_BUTTRATE <= new_rate <= UPPER_LIMIT_BUTTRATE:
                    settings["rate"] = new_rate
                    modify_streamer_values(
                        JSON_DATA_PATH, ctx.author.name, "rate", new_rate)
                    await ctx.channel.send(f'Rate{" for the channel" + channel_name if is_in_bot_channel else ""} changed to {new_rate}.')
                else:
                    await ctx.channel.send(
                        f'{new_rate} is not a valid rate. Please choose a number between 10 and 1000.')

    @commands.command(name="buttword", aliases=["setword"])
    async def buttword(self, ctx: commands.Context, new_word: str = None):
        # Do command for the user's channel instead of channel done in if it's the bot's channel
        is_in_bot_channel, channel_name = in_bot_channel(bot_nickname, ctx.author.name, ctx.channel.name)

        # If the user is in the bot's channel and checking for their own but has not joined the channel,
        # let the user know of that instead
        if is_in_bot_channel and channel_name not in self.channel_settings:
            await ctx.channel.send(
                'The bot has not joined your channel, do !join to have it join.')
        else:
            # Get logger for the current channel
            logger = get_logger_for_channel(channel_name)
            settings = self.channel_settings.setdefault(
                channel_name, DEFAULT_BUTT_INFO)
            # if an argument isn't specified
            if new_word is None:
                await ctx.channel.send(f'The current word for the channel {channel_name} is {settings["word"]}.')
            else:
                # check if the user has permission to change the word
                if channel_name != ctx.author.name:
                    await ctx.channel.send('You can only change the word for your own channel.')
                    logger.warning(
                        f"{ctx.author.name} tried to change the word for {channel_name}")
                    return
                settings["word"] = new_word
                modify_streamer_values(
                    JSON_DATA_PATH, channel_name, "word", new_word)
                await ctx.channel.send(f'Word {" for the channel" + channel_name if is_in_bot_channel else ""} changed to {new_word}.')

                logger.info(
                    f"Word changed to {settings['word']} for channel: {channel_name}")

    @commands.command()
    async def ignoreme(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        user_to_ignore = ctx.author.name

        # Adds user to the ignore list
        worked = add_ignore_list(IGNORED_LIST_PATH, user_to_ignore)
        if worked:
            await ctx.channel.send(f'User {user_to_ignore} has been successfully ignored.')
            logger.info(f"User {user_to_ignore} ignored")
        else:
            await ctx.channel.send(f'User {user_to_ignore} has already been ignored.')

    @commands.command()
    async def unignoreme(self, ctx: commands.Context):
        # Get logger for the current channel
        logger = get_logger_for_channel(ctx.channel.name)
        user_to_ignore = ctx.author.name

        # Removes user from the ignore list
        worked = remove_ignore_list(IGNORED_LIST_PATH, user_to_ignore)
        if worked:
            await ctx.channel.send(f'User {user_to_ignore} has been successfully unignored.')
            logger.info(f"User {user_to_ignore} unignored")
        else:
            await ctx.channel.send(f'User {user_to_ignore} is currently not ignored.')


def main():
    if os.path.exists(JSON_DATA_PATH):
        with open(JSON_DATA_PATH, "r", encoding="utf8") as json_file:
            settings = json.load(json_file)
    else:
        settings = {}
        settings[bot_nickname] = DEFAULT_BUTT_INFO

    # You can set up a general logger for the bot if needed
    logger = get_logger_for_channel("bot")
    logger.info(f'current settings: {settings}')
    logger.info('successfully loaded settings...')
    bot = Bot(settings)
    bot.run()


if __name__ == "__main__":
    main()
