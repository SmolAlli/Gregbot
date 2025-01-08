
import math
import os
from json_funcs import modify_streamer_settings, modify_streamer_values
from ignore_these_words import IGNORE_WORDS
from twitchio.ext import commands  # type: ignore
import random
from syllafunc import syllables_split, syllables_to_sentence
from dotenv import load_dotenv
import json

load_dotenv()
access_token = os.environ.get('TMI_TOKEN')

# json containing settings for each streamer
json_data_path = "streamer_settings.json"
# 1 BUTT per this many words
BUTT_RATE_PER_SENTENCE = 10
UPPER_LIMIT_BUTTRATE = 1000
LOWER_LIMIT_BUTTRATE = 10


class Bot(commands.Bot):

    def __init__(self, data: dict):
        super().__init__(token=access_token, prefix='!',
                         initial_channels=list(data.keys()))
        # Store settings per channel
        self.channel_settings: dict = data

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

        # Ensure bot's nick is in the channel settings with default values
        if self.nick not in self.channel_settings:
            print(f'Adding bot {self.nick} to settings with default values...')
            self.channel_settings[self.nick] = {"rate": 30, "word": "BUTT"}

            # Save the updated settings back to the JSON file
            modify_streamer_settings(json_data_path, "add", {
                                     self.nick: self.channel_settings[self.nick]})

        print(f'channels connected to: {list(self.channel_settings.keys())}')

    async def event_command_error(self, ctx, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f'Wait a couple of seconds before sending something else, {ctx.author.name}!')

    async def event_message(self, message):
        if message.echo:
            return

        print(message.author.name, ':', message.content)

        # Get or initialize settings for this channel
        channel_name = message.channel.name
        settings = self.channel_settings.get(channel_name)
        random_int = random.randint(1, settings["rate"])
        print('random num:', random_int, '| target: 1')
        if settings and random_int == 1:
            syllable_lists = syllables_split(message.content)
            butt_num = math.ceil(len(syllable_lists) / BUTT_RATE_PER_SENTENCE)

            for num in range(butt_num):
                # pick a random word to replace
                random_word = random.randint(0, len(syllable_lists) - 1)
                # ignore some words, they don't work well with the BUTT replacement
                # you can find those words in ignore_these_words.py
                attempts = 0
                # if there's only 1 syllable and it's in the ignore list, try a different one
                # give it a few attempts to find one
                while len(syllable_lists[random_word]) <= 1 and syllable_lists[random_word][0].lower() in IGNORE_WORDS and attempts < 10:
                    random_word = random.randint(0, len(syllable_lists) - 1)
                    attempts += 1
                    if attempts >= 9:
                        print('Could not find a word to replace.')
                        return
                print('replacing word', syllable_lists[random_word])
                # pick a random syllable in the word to replace
                random_syllable = random.randint(
                    0, len(syllable_lists[random_word]) - 1)
                # replace the syllable with the streamer's chosen word
                syllable_lists[random_word][random_syllable] = settings["word"]
            # Bot sends the new sentence to the chat
            await message.channel.send(f'{syllables_to_sentence(syllable_lists)}')

        await self.handle_commands(message)

    @commands.command()
    @commands.cooldown(3, 45, commands.Bucket.user)
    async def hello(self, ctx: commands.Context):
        await ctx.channel.send(f'Hello {ctx.author.name}!')

    @commands.command()
    async def join(self, ctx: commands.Context):
        # Use the name of the user who invoked the command
        channel_name = ctx.author.name

        if channel_name not in self.channel_settings:
            # Set default values for the new channel
            self.channel_settings[channel_name] = {"rate": 30, "word": "BUTT"}
            # add entry to json data
            modify_streamer_settings(json_data_path, "add",
                                     {channel_name: self.channel_settings.get(channel_name)})

            await ctx.send(f'Joining {channel_name}\'s channel')
            await self.join_channels([channel_name])
        else:
            await ctx.send(f'Already in {channel_name}\'s channel.')

    @commands.command()
    async def leave(self, ctx: commands.Context):
        # Use the name of the user who invoked the command
        channel_name = ctx.author.name

        if channel_name != ctx.channel.name:
            print('Non-host trying to leave channel.')
            return

        if channel_name in self.channel_settings:

            modify_streamer_settings(json_data_path, "rm", {
                                     channel_name: self.channel_settings[channel_name]})
            del self.channel_settings[channel_name]

            await ctx.send(f'Leaving {channel_name}\'s channel.')
            await self.part_channels([channel_name])
        else:
            await ctx.send(f'The bot is not currently in {channel_name}\'s channel.')

    @commands.command()
    async def buttrate(self, ctx: commands.Context, new_rate: str = None):
        message_user_name = ctx.author.name
        channel_name = ctx.channel.name
        settings = self.channel_settings.setdefault(
            message_user_name, {"rate": 30, "word": "BUTT"})

        if new_rate is None:
            if message_user_name != channel_name:
                print(
                    f'{message_user_name} tried to check the rate of {channel_name}')
                return
            await ctx.channel.send(f'The current rate is {settings["rate"]}.')
        else:
            if message_user_name != channel_name:
                print(
                    f'{message_user_name} tried to change the rate of {channel_name}')
                return
            try:
                new_rate = int(new_rate)
                if LOWER_LIMIT_BUTTRATE <= new_rate <= UPPER_LIMIT_BUTTRATE:
                    settings["rate"] = new_rate

                    modify_streamer_values(
                        json_data_path, message_user_name, "rate", new_rate)

                    await ctx.channel.send(f'Rate set to {new_rate}.')
                else:
                    await ctx.channel.send(f'{new_rate} is not a valid rate. Please choose a number between 10 and 1000.')
            except ValueError:
                await ctx.channel.send(f'"{new_rate}" is not a valid number. Please enter a valid number between 10 and 1000.')

    @commands.command()
    async def buttword(self, ctx: commands.Context, new_word: str = None):
        channel_name = ctx.channel.name
        settings = self.channel_settings.setdefault(
            channel_name, {"rate": 30, "word": "BUTT"})

        if new_word is None:
            await ctx.channel.send(f'The current word for this channel is {settings["word"]}.')
        else:
            if channel_name != ctx.author.name:
                await ctx.channel.send(f'You can only change the word for your own channel.')
                return
            settings["word"] = new_word
            modify_streamer_values(
                json_data_path, channel_name, "word", new_word)
            await ctx.channel.send(f'Word for this channel changed to {settings["word"]}.')


def main():
    if os.path.exists(json_data_path):
        with open(json_data_path, "r") as json_file:
            settings = json.load(json_file)
    else:
        settings = {}

    print(f'current settings: {settings}')
    print(f'successfully loaded settings...')
    bot = Bot(settings)
    bot.run()


if __name__ == "__main__":
    main()
