from discord.ext import commands
import requests
import json
import time
from bs4 import BeautifulSoup
from fake_headers import Headers
from prettytable import PrettyTable
from prettytable import DOUBLE_BORDER


class Modulos(commands.Cog):
    '''Comandos principais do BOT'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='resumo',
                      help='''
    Pega o resumo de heróis mais jogados.
    Argumento: community ID / steamID / steamID32 / steamID64 / steamID3
     / Steam URL / DotaBuff URL / DotaMax URL
    Ex.: .resumo 86731165
         .resumo 76561198046996893
         .resumo https://pt.dotabuff.com/players/86731165
         .resumo https://steamcommunity.com/id/dancaffrey'''
                      )
    async def resumo(self, ctx, idsteam):
        url = f'https://steamid.xyz/{idsteam}'
        headers = Headers().generate()
        resp = requests.get(url, headers=headers)
        site = BeautifulSoup(resp.content, 'html.parser')

        idsteam = site.find('input', type="text",
                            value=True).find_next().find_next().attrs

        nome = site.find('input', type="text", value=True).find_next(
        ).find_next().find_next().find_next().attrs

        idsteam = idsteam['value']
        nome = nome['value']

        url = (f'https://api.opendota.com/api/players/{idsteam}/wl')
        data = requests.get(url)
        perfil = json.loads(data.text)
        win = perfil["win"]
        lose = perfil["lose"]
        tabela_apresentacao = PrettyTable()
        tabela_apresentacao.set_style(DOUBLE_BORDER)
        tabela_apresentacao.left_padding_width = 1
        tabela_apresentacao.right_padding_width = 1
        tabela_apresentacao.align = "c"
        tabela_apresentacao.field_names = [f'Olá {nome}, bem-vindo ao Oracle!']

        try:
            winrate = (perfil['win']/(perfil['win']+perfil['lose']))*100
            tabela_apresentacao.add_row([
                f'Atualmente você está com {win} vitórias e {lose} derrotas'
                f' o que resulta em {winrate:.2f}% de winrate.'])
        except ZeroDivisionError:
            ...

        tabela_apresentacao.add_row(['Este são seus heróis mais jogados:'])

        url = ('https://api.opendota.com/api/heroes')
        data = requests.get(url)
        herois = json.loads(data.text)
        url = (f'https://api.opendota.com/api/players/{idsteam}/heroes')
        data = requests.get(url)
        resumo = json.loads(data.text)

        tabela_resumo = PrettyTable()
        tabela_resumo.field_names = ['Heróis', 'Total', 'Winrate', 'Vitórias',
                                     'Derrotas', 'Última Partida']
        tabela_resumo.set_style(DOUBLE_BORDER)
        tabela_resumo.left_padding_width = 1
        tabela_resumo.right_padding_width = 1
        tabela_resumo.align = "c"
        tabela_resumo.align["Heróis"] = "l"

        for i in range(len(resumo)):
            try:
                winrate = f"{(resumo[i]['win']/resumo[i]['games'])*100: .1f}"
            except ZeroDivisionError:
                # Apenas ignorar o erro de divisão por 0
                ...
            vitorias = str(resumo[i]['win'])
            derrotas = str(resumo[i]['games']-resumo[i]['win'])
            total = str(resumo[i]['games'])
            ultima_partida = time.strftime(
                '%d-%m-%Y', time.localtime(resumo[i]['last_played']))
            for x in range(len(herois)):
                if int(resumo[i]['hero_id']) == herois[x]['id']:
                    heroi = herois[x]['localized_name']
            if i > 19:
                break

            tabela_resumo.add_row([heroi, total, winrate, vitorias,
                                   derrotas, ultima_partida])
        await ctx.author.send(
            f'```{tabela_apresentacao.get_string()}```', delete_after=120)
        await ctx.author.send(
            f'```{tabela_resumo.get_string()}```', delete_after=120)

    @commands.command(name='meta',
                      help='''
    Pega a "%" de winrate de cada herói em cada rank.
    Argumento: rank (Arauto / Guardião / Cruzado / Arconte / \
                     Lenda / Ancestral / Divino / Imortal)
    Ex.: .meta lenda
         .meta arauto
         .meta imortal'''
                      )
    async def meta(self, ctx, rank):

        url = ('https://api.opendota.com/api/heroStats')
        data = requests.get(url)
        meta = json.loads(data.text)

        tabela_meta = PrettyTable()
        tabela_meta.field_names = ['Herói', 'Arauto', 'Guardião', 'Cruzado',
                                   'Arconte', 'Lenda', 'Ancestral', 'Divino',
                                   'Imortal']

        tabela_meta.set_style(DOUBLE_BORDER)
        tabela_meta.left_padding_width = 1
        tabela_meta.right_padding_width = 1
        tabela_meta.align["Herói"] = "l"
        tabela_meta.align = "c"
        tabela_meta.sortby = rank.title()
        tabela_meta.reversesort = True

        for i in range(len(meta)):
            arauto = f"{(meta[i]['1_win']/meta[i]['1_pick'])*100:.1f}%"
            guardiao = f"{(meta[i]['2_win']/meta[i]['2_pick'])*100:.1f}%"
            cruzado = f"{(meta[i]['3_win']/meta[i]['3_pick'])*100:.1f}%"
            arconte = f"{(meta[i]['4_win']/meta[i]['4_pick'])*100:.1f}%"
            lenda = f"{(meta[i]['5_win']/meta[i]['5_pick'])*100:.1f}%"
            ancestral = f"{(meta[i]['6_win']/meta[i]['6_pick'])*100:.1f}%"
            divino = f"{(meta[i]['7_win']/meta[i]['7_pick'])*100:.1f}%"
            imortal = f"{(meta[i]['8_win']/meta[i]['8_pick'])*100:.1f}%"

            heroi = meta[i]['localized_name']
            tabela_meta.add_row([f'{heroi:<20}', arauto,
                                 guardiao, cruzado, arconte, lenda, ancestral,
                                 divino, imortal])

        # Adicionar mais linhas quando lançar mais heróis
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=0, end=14)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=15, end=29)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=30, end=44)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=45, end=59)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=60, end=74)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=75, end=89)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=90, end=104)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=105, end=119)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_meta.get_string(start=120)}```',
            delete_after=120)

    @commands.command(name='recentes',
                      help='''
    Pega informações detalhadas das ultimas 20 partidas jogadas.
    Argumento: community ID / steamID / steamID32 / steamID64 / steamID3
     / Steam URL / DotaBuff URL / DotaMax URL
    Ex.: .recentes 86731165
         .recentes 76561198046996893
         .recentes https://pt.dotabuff.com/players/86731165
         .recentes https://steamcommunity.com/id/dancaffrey'''
                      )
    async def recentes(self, ctx, idsteam):
        url = f'https://steamid.xyz/{idsteam}'
        headers = Headers().generate()
        resp = requests.get(url, headers=headers)
        site = BeautifulSoup(resp.content, 'html.parser')

        idsteam = site.find('input', type="text",
                            value=True).find_next().find_next().attrs

        idsteam = idsteam['value']

        url = ('https://api.opendota.com/api/heroes')
        data = requests.get(url)
        herois = json.loads(data.text)

        url = (f'https://api.opendota.com/api/players/{idsteam}/recentMatches')
        data = requests.get(url)
        partidas = json.loads(data.text)

        tabela_recentes = PrettyTable()
        tabela_recentes.field_names = ['Herói', 'Resultado', 'K', 'D', 'A',
                                       'XP/min', 'G/min', 'DanoHeróis',
                                       'DanoTorres', 'Creeps',
                                       'Tempo', 'ID Partida',
                                       'Data']
        tabela_recentes.set_style(DOUBLE_BORDER)
        tabela_recentes.left_padding_width = 1
        tabela_recentes.right_padding_width = 1
        tabela_recentes.align["Herói"] = "l"
        tabela_recentes.align = "c"

        for i in range(len(partidas)):
            xpmin = partidas[i]['xp_per_min']
            goldmin = str(partidas[i]['gold_per_min'])
            dano_em_herois = partidas[i]['hero_damage']
            dano_em_torres = partidas[i]['tower_damage']
            last_hits = partidas[i]['last_hits']
            id_partida = partidas[i]['match_id']
            duracao = int(partidas[i]['duration']/60)
            kills = partidas[i]['kills']
            deaths = partidas[i]['deaths']
            assists = partidas[i]['assists']
            data_horario = time.strftime(
                '%d-%m-%y', time.localtime(partidas[i]['start_time']))
            for x in range(len(herois)):
                if partidas[i]['hero_id'] == herois[x]['id']:
                    heroi = herois[x]['localized_name']
            if partidas[i]['player_slot'] <= 127\
                    and partidas[i]['radiant_win'] is True:
                resultado = 'Vitória'
            elif partidas[i]['player_slot'] <= 127\
                    and partidas[i]['radiant_win'] is False:
                resultado = 'Derrota'
            elif partidas[i]['player_slot'] > 127\
                    and partidas[i]['radiant_win'] is False:
                resultado = 'Vitória'
            elif partidas[i]['player_slot'] > 127\
                    and partidas[i]['radiant_win'] is True:
                resultado = 'Derrota'

            tabela_recentes.add_row([f'{heroi:<20}', resultado, kills, deaths,
                                    assists, xpmin, goldmin, dano_em_herois,
                                    dano_em_torres, last_hits,
                                    duracao, id_partida,
                                    data_horario])

        await ctx.author.send(
            f'```{tabela_recentes.get_string(start=0, end=10)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_recentes.get_string(start=11)}```',
            delete_after=120)

    @commands.command(name='ultimas',
                      help='''
    Pega informações simplificadas das ultimas 200 partidas jogadas.
    Argumentos: community ID / steamID / steamID32 / steamID64 / steamID3
     / Steam URL / DotaBuff URL / DotaMax URL
    Ex.: .ultimas 86731165
                      '''
                      )
    async def ultimas(self, ctx, idsteam):

        url = f'https://steamid.xyz/{idsteam}'
        headers = Headers().generate()
        resp = requests.get(url, headers=headers)
        site = BeautifulSoup(resp.content, 'html.parser')

        idsteam = site.find('input', type="text",
                            value=True).find_next().find_next().attrs

        idsteam = idsteam['value']

        url = ('https://api.opendota.com/api/heroes')
        data = requests.get(url)
        herois = json.loads(data.text)

        url = (f'https://api.opendota.com/api/players/{idsteam}/recentMatches')
        data = requests.get(url)
        partidas = json.loads(data.text)

        url = (f'https://api.opendota.com/api/players/{idsteam}/matches')
        data = requests.get(url)
        partidas = json.loads(data.text)

        tabela_todas = PrettyTable()
        tabela_todas.field_names = ['Heróis', 'Resultados', 'K', 'D', 'A',
                                    'Grupo', 'Duração', 'ID da Partida',
                                    'Data e Horário']
        tabela_todas.set_style(DOUBLE_BORDER)
        tabela_todas.left_padding_width = 1
        tabela_todas.right_padding_width = 1
        tabela_todas.align["Herói"] = "l"
        tabela_todas.align = "c"

        for i in range(len(partidas)):
            id_partida = partidas[i]['match_id']
            duracao = int(partidas[i]['duration']/60)
            kills = partidas[i]['kills']
            deaths = partidas[i]['deaths']
            assists = partidas[i]['assists']
            tamanho_grupo = partidas[i]['party_size']
            data_horario = time.strftime(
                '%d-%m-%Y %H:%M:%S', time.localtime(partidas[i]['start_time']))

            for x in range(len(herois)):
                if partidas[i]['hero_id'] == herois[x]['id']:
                    heroi = herois[x]['localized_name']

            if partidas[i]['player_slot'] <= 127\
                    and partidas[i]['radiant_win'] is True:
                resultado = 'Vitória'
            elif partidas[i]['player_slot'] <= 127\
                    and partidas[i]['radiant_win'] is False:
                resultado = 'Derrota'
            elif partidas[i]['player_slot'] > 127\
                    and partidas[i]['radiant_win'] is False:
                resultado = 'Vitória'
            elif partidas[i]['player_slot'] > 127\
                    and partidas[i]['radiant_win'] is True:
                resultado = 'Derrota'

            if i > 220:
                break

            tabela_todas.add_row(
                [f'{heroi:<20}', resultado, kills, deaths,
                 assists, tamanho_grupo, duracao, id_partida,
                 data_horario])

        await ctx.author.send(
            f'```{tabela_todas.get_string(start=0, end=14)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=15, end=29)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=30, end=44)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=45, end=59)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=60, end=74)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=75, end=89)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=90, end=104)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=105, end=119)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=120, end=134)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=135, end=149)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=150, end=164)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=165, end=179)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=180, end=194)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=195, end=209)}```',
            delete_after=120)
        await ctx.author.send(
            f'```{tabela_todas.get_string(start=210)}```',
            delete_after=120)

    @commands.command(name='builds',
                      help='''
    Pega itens mais usados para cada herói em partidas acima de 7k MMR
    Argumento: herói (coloque o nome do herói como: templar, não: lanaya)
    Ex.: .builds lone
         .builds anti
         .builds sky'''
                      )
    async def builds(self, ctx, heroi):
        url = ('https://api.opendota.com/api/heroes')
        data = requests.get(url)
        herois = json.loads(data.text.lower())

        with open('item_ids.json', 'r', encoding='utf8') as t:
            tabela_itens = json.load(t)

        tabela = PrettyTable()
        tabela.field_names = ['Melhores itens para cada herói!']
        tabela.set_style(DOUBLE_BORDER)
        tabela.left_padding_width = 1
        tabela.right_padding_width = 1
        tabela.align = "c"

        for x in range(len(herois)):
            if heroi.lower() in herois[x]['localized_name']:
                id = herois[x]['id']
                nome = herois[x]['localized_name']
                tabela = PrettyTable()
                tabela.field_names = ['Esses são os itens mais usados para:']
                tabela.add_row([f'{nome.title()}'])
                tabela.set_style(DOUBLE_BORDER)
                await ctx.author.send(f'```{tabela.get_string()}```',
                                      delete_after=120)

        url_itens = (
            f'https://api.opendota.com/api/heroes/{id}/itemPopularity')
        data_itens = requests.get(url_itens)
        itens = json.loads(data_itens.text)

        start = []
        early = []
        mid = []
        late = []

        for i in itens['start_game_items'].keys():
            start.append(i)

        for i in itens['early_game_items'].keys():
            early.append(i)

        for i in itens['mid_game_items'].keys():
            mid.append(i)

        for i in itens['late_game_items'].keys():
            late.append(i)

        itens_start = []
        itens_early = []
        itens_mid = []
        itens_late = []

        for keys in tabela_itens.keys():
            for valor in range(len(start)):
                if start[valor] == keys:
                    itens_start.append(
                        tabela_itens[keys].title().replace('_', ' '))

        for keys in tabela_itens.keys():
            for valor in range(len(early)):
                if early[valor] == keys:
                    itens_early.append(
                        tabela_itens[keys].title().replace('_', ' '))

        for keys in tabela_itens.keys():
            for valor in range(len(mid)):
                if mid[valor] == keys:
                    itens_mid.append(
                        tabela_itens[keys].title().replace('_', ' '))

        for keys in tabela_itens.keys():
            for valor in range(len(late)):
                if late[valor] == keys:
                    itens_late.append(
                        tabela_itens[keys].title().replace('_', ' '))

        tabela_itens_start = PrettyTable()
        tabela_itens_start.add_column("Itens Iniciais", itens_start)
        tabela_itens_start.set_style(DOUBLE_BORDER)
        tabela_itens_start.left_padding_width = 1
        tabela_itens_start.right_padding_width = 1
        tabela_itens_start.align = "l"

        tabela_itens_early = PrettyTable()
        tabela_itens_early.add_column("Itens Começo", itens_early)
        tabela_itens_early.set_style(DOUBLE_BORDER)
        tabela_itens_early.left_padding_width = 1
        tabela_itens_early.right_padding_width = 1
        tabela_itens_early.align = "l"

        tabela_itens_mid = PrettyTable()
        tabela_itens_mid.add_column("Itens Meio", itens_mid)
        tabela_itens_mid.set_style(DOUBLE_BORDER)
        tabela_itens_mid.left_padding_width = 1
        tabela_itens_mid.right_padding_width = 1
        tabela_itens_mid.align = "l"

        tabela_itens_late = PrettyTable()
        tabela_itens_late.add_column("Itens Final", itens_late)
        tabela_itens_late.set_style(DOUBLE_BORDER)
        tabela_itens_late.left_padding_width = 1
        tabela_itens_late.right_padding_width = 1
        tabela_itens_late.align = "l"

        await ctx.author.send(f'```{tabela_itens_start.get_string()}```',
                              delete_after=120)
        await ctx.author.send(f'```{tabela_itens_early.get_string()}```',
                              delete_after=120)
        await ctx.author.send(f'```{tabela_itens_mid.get_string()}```',
                              delete_after=120)
        await ctx.author.send(f'```{tabela_itens_late.get_string()}```',
                              delete_after=120)

    @commands.command(name='amigos',
                      help='''
    Pega informações de partidas jogadas com amigos.
    Argumento: community ID / steamID / steamID32 / steamID64 / steamID3
     / Steam URL / DotaBuff URL / DotaMax URL
    Ex.: .amigos 86731165
         .amigos 76561198046996893
         .amigos https://pt.dotabuff.com/players/86731165
         .amigos https://steamcommunity.com/id/dancaffrey'''
                      )
    async def amigos(self, ctx, idsteam):

        url = f'https://steamid.xyz/{idsteam}'
        headers = Headers().generate()
        resp = requests.get(url, headers=headers)
        site = BeautifulSoup(resp.content, 'html.parser')

        idsteam = site.find('input', type="text",
                            value=True).find_next().find_next().attrs

        idsteam = idsteam['value']

        url = (f'https://api.opendota.com/api/players/{idsteam}/peers')
        data = requests.get(url)
        amigos = json.loads(data.text)

        tabela_amigos = PrettyTable()
        tabela_amigos.field_names = ['Nome', 'Total', 'Winrate',
                                     'Vitórias', 'Derrotas', 'ID',
                                     'Última Juntos']
        tabela_amigos.set_style(DOUBLE_BORDER)
        tabela_amigos.left_padding_width = 1
        tabela_amigos.right_padding_width = 1
        tabela_amigos.align = "l"

        for i in range(len(amigos)):
            nome = amigos[i]['personaname']
            winrate = f"{(amigos[i]['win']/amigos[i]['games'])*100: .1f}"
            total = amigos[i]['games']
            win = str(amigos[i]['win'])
            lose = str(amigos[i]['games'] -
                       amigos[i]['win'])
            id_conta = amigos[i]['account_id']
            ultima_juntos = time.strftime(
                '%H:%M %d-%m-%Y', time.localtime(amigos[i]['last_played']))

            tabela_amigos.add_row(
                [nome, total, winrate, win, lose, id_conta, ultima_juntos])

            if i > 25:
                break

        await ctx.author.send(
            f'```{tabela_amigos.get_string(start=0, end=15)}```',
            delete_after=120)


def setup(bot):
    bot.add_cog(Modulos(bot))
