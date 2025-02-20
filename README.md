## Personal Buttsbot to replace the depreciated version.

### Twitch chatbot that grabs a random user's message, randomly replaces syllables with the word "butt" (by default), and spits the message back out.

### Common Commands:

- !join - Summons the bot to the user's channel (typed in the bot's chat)
- !leave - Dismiss ButtsBorg (typed in the broadcaster's chat)
- !buttword [word] - Replaces the current word with the given parameter. If no parameter given, will display the current word. Default is 'butt'.
- !buttrate [rate] - Replaces the current rate with the given parameter. Must be an integer from 10 to 1000. If no parameter given, will display the current rate. Default is 30 (representing 1/30 chance)
- !ignoreme - Ignores all messages and will not butt-ify you
- !unignoreme - Removes ignore from you

### Random Word List Commands:

- !togglerandomwords - enable/disable your random word list
- !randomwords - display your current word list
- !addword (word) - add a word to the list
- !removeword (word) - delete a word from your current list

### February 2025 Updates:

- Streamers can now create a list of replacement words that will randomly be chosen from. The list will only be active if the streamer enables their `!togglerandomwords` setting (See commands above ^).
- Buttwords will now follow capitalization of the original word/syllable replaced.
- Buttwords can no longer replace single syllable/word messages.

### January 2025 Updates:

- Remove the chance of auxillary verbs being replaced (in most cases it doesn't work too well)
- Improve the illegal word list
- Only the streamer can use !buttrate
- Global vars for upper/lower buttrate limits and BUTTs per sentence
- Better documentation of the message and word/syllable replacement process
- Added a logging feature for each stream that uses the bot. Will help for identifying bugs and fixing any errors.
- Handle strings that have symbols attached to them better (also won't replace single-symbol syllables)
- Protection to prevent the bot from getting too unlucky (If the rate is 1/30 messages and the rate has been passed, every next chat message will lower the rate by 1 until the bot responds)
- Handle plurals

### Soon/To-Do/Ideas:

- Add a !pause command so the user can keep their settings but pause the bot from responding
- Better word/syllable selection for multiple BUTTs in a sentence (i.e. make sure they aren't side by side). Might need to look into other ways/packages
- Allow specific words/syllables to get replaced before others and allow streamers to set those
- Allow chatters to favorite a previously generated sentence
- Command to show a chatter how many times the bot has gotten them
- ignore other bots(?)

## Running

- Use python >=3.9
- Install dependencies with `pip install -r requirements.txt`
- Setup your .env file with your channel's token/names (refer to the .env sample file) - access token info here -> https://twitchio.dev/en/stable/quickstart.html#tokens-and-scopes
- Run with `py bot.py`
