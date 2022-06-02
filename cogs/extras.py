import discord
from discord.ext import commands


class Extras(commands.Cog):
    '''Comandos extras do BOT'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        status = discord.Game("Trabalhando com API's de DotA 2")
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=status
        )
        print(f'Bot ligado! Conectado como {self.bot.user}!')

    @commands.command(name='ping',
                      help='Mostra o ping atual')
    async def ping(self, ctx):
        ping = round(self.bot.latency*1000)
        if ping > 100:
            await ctx.send(
                f'Você está com {ping}ms de ping. Assim você só vai feedar!'
            )
        elif ping < 100:
            await ctx.send(
                f'Você está com {ping}ms de ping. Bora matar geral!'
            )

    @commands.command(name='limpar',
                      help='Limpa as mensagens em um chat no Discord')
    @commands.has_permissions(manage_messages=True)
    async def limpar(self, ctx, amount=1000):
        await ctx.channel.purge(limit=amount)


def setup(bot):
    bot.add_cog(Extras(bot))
