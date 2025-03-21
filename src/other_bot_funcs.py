def in_bot_channel(bot_nickname: str, message_username: str, channel_name: str) -> tuple[bool, str]:
    """
    This function takes in three arguments: `botNickname`, `messageUserName`, and `channelName`.

    `botNickname` should be the global name of the bot (`bot_nickname`).

    `messageUsername` should be the name of the message sender (`ctx.author.name`)

    `channelName` should be the name of the channel that the message was sent in (`ctx.channel.name`)

    The return type is a tuple that contains a `bool` and `str`.

    The `bool` references whether or not the message is being sent in the bot's channel.

    the `str` references the channel that the bot is connected to and will make changes to.

    """
    is_in_bot_channel = channel_name == bot_nickname
    channel_name = message_username if is_in_bot_channel else channel_name

    return is_in_bot_channel, channel_name
