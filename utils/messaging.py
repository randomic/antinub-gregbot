"""
Contains utilities regarding messages
"""


def paginate(string, pref='```\n', aff='```', max_length=2000, sep='\n'):
    'Chop a string into even chunks of max_length around the given separator'
    max_size = max_length - len(pref) - len(aff)

    str_length = len(string)
    if str_length <= max_size:
        return [pref + string + aff]
    else:
        split = string.rfind(sep, 0, max_size) + 1
        if split:
            return ([pref + string[:split] + aff]
                    + paginate(string[split:], pref, aff, max_length, sep))
        else:
            return ([pref + string[:max_size] + aff]
                    + paginate(string[max_size:], pref, aff, max_length, sep))


async def notify_owner(bot, messages):
    'Send message to the private channel of the owner'
    channel = await bot.get_user_info(bot.config.get('owner_id'))
    for message in messages:
        await bot.send_message(channel, message)


async def message_input(ctx, prompt, timeout=60):
    message = await ctx.bot.say(prompt)
    password = await ctx.bot.wait_for_message(
        timeout=timeout,
        author=ctx.message.author,
        channel=ctx.message.channel)
    if not password:
        await ctx.bot.edit_message(
            message,
            new_content='Timed out, cancelling.')
    return password
