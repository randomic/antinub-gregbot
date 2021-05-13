"""
Contains utilities regarding messages
"""
from math import ceil


class Paginate:
    'Chop a string into even chunks of max_length around the given separator'
    def __init__(self, string, enclose=('```\n', '```'),
                 page_size=2000, separator='\n'):
        self._string = string
        self._prefix = enclose[0]
        self._affix = enclose[1]
        self._size = page_size - len(self._prefix) - len(self._affix)
        self._separator = separator

        self._r_seek = len(string)
        self._pages_yielded = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._r_seek <= 0:
            raise StopIteration()

        self._pages_yielded += 1
        if self._r_seek <= self._size:
            string = self._wrap_string(-self._r_seek)
            self._r_seek = 0
            return string

        split = self._string.rfind(
            self._separator, -self._r_seek, self._size - self._r_seek
        ) + 1
        if split:
            string = self._wrap_string(-self._r_seek, split)
            self._r_seek -= len(string) - len(self._prefix) - len(self._affix)
        else:
            string = self._wrap_string(
                -self._r_seek, self._size - self._r_seek
            )
            self._r_seek -= self._size

        return string

    def _wrap_string(self, start, stop=None):
        return self._prefix + self._string[start:stop] + self._affix

    def prefix_next(self, prefix):
        'Return next page prefixed but still smaller than page_size'
        old_size = self._size
        self._size -= len(prefix)
        string = self.__next__()
        self._size = old_size
        return prefix + string

    @property
    def pages_yielded(self):
        'Return the number of pages yielded by the iterator so far'
        return self._pages_yielded

    @property
    def pages_left(self):
        'Return number of remaining pages if the iterator is called normally'
        return ceil(self._r_seek / self._size)


async def notify_owner(bot, messages):
    'Send message to the private channel of the owner'
    user = await bot.fetch_user(bot.config['owner_id'])
    for message in messages:
        await user.send(message)


async def message_input(ctx, prompt, timeout=60):
    'Prompt user for input and wait for response or timeout'
    message = await ctx.bot.say(prompt)
    user_input = await ctx.bot.wait_for_message(
        timeout=timeout,
        author=ctx.message.author,
        channel=ctx.message.channel)
    if not user_input:
        await ctx.bot.edit_message(
            message,
            new_content='Timed out, cancelling.')
    return user_input
