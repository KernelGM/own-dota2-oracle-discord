import os
from discord.ext import commands
from decouple import config


bot = commands.Bot(command_prefix='.')


@bot.command(name='carregar', help='''
Comando usado para carregar as funcionalidades do BOT.'''
             )
async def carregar(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Extensão {extension} adicionada com sucesso!')


@bot.command(name='remover', help='''
Comando usado para remover as funcionalidades do BOT.'''
             )
async def remover(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Extensão {extension} removida com sucesso!')


@bot.command(name='recarregar', help='''
Comando usado para recarregar as funcionalidades do BOT.'''
             )
async def recarregar(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Extensão {extension} recarregada com sucesso!')

for arquivo in os.listdir(os.getcwd()+'/cogs'):
    if arquivo.endswith('.py'):
        bot.load_extension(f'cogs.{arquivo[:-3]}')


SECRET_KEY = config('TOKEN')
bot.run(SECRET_KEY)
