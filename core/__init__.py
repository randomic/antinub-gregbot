"""
Set up core extensions
"""
from .control import Control


def setup(bot):
    """Add core cogs to bot.

    """
    bot.add_cog(Control(bot))
