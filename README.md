## Personal Buttsbot to replace the depreciated version.

### Twitch chatbot that copy's a random user's message, randomly replaces syllables with the word "BUTT" (by default), and spits the message back out.

### Commands:
- !join - Summons the bot to the user's channel (typed in the bot's chat)
- !leave - Dismiss ButtsBorg (typed in the broadcaster's chat)
- !buttword - Displays the current word being used ('BUTT' is DEFAULT)
- !buttword (word) - replaces the current word with the newly typed one
- !rate - Displays the rate at how many messages will pass before you can expect a response (30 is DEFAULT)
- !rate (number from 10-1000)
- !ignoreme - Ignores all messages and will not butt-ify you
- !unignoreme - Removes ignore from you

### Recent Updates:
-  Remove the chance of auxillary verbs being replaced (in most cases it doesn't work too well)
-  Improve the illegal word list
-  Only the streamer can use !buttrate
-  Global vars for upper/lower buttrate limits and BUTTs per sentence
-  Better documentation of the message and word/syllable replacement process
-  Added a logging feature for each stream that uses the bot. Will help for identifying bugs and fixing any errors.
-  Handle strings that have symbols attached to them better (also won't replace single-symbol syllables)

### Soon/To-Do:
- Add a !pause command so the user can keep their settings but pause the bot from responding
- Better word/syllable selection for multiple BUTTs in a sentence (i.e. make sure they aren't side by side). Might need to look into other ways/packages
- Maybe have cases for specific words that get replaced
- Handle plurals

## Running

-   Install dependencies with `pip install -r requirements.txt`
-   Setup your .env file with your channel's token/names (refer to the .env sample file)
-   Run with `py bot.py`
