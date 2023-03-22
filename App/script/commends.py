import discord

from objects import *


async def check_commend_format(self: object, help_content: str, length: int or tuple(int, int)):
    if len(self.mess) > 1 and self.mess[1] in ['-h', '-help', '--help', 'help']:
        await self.message.channel.send(
            embed=discord.Embed(title=f'Usage: *{help_content}*!',
                                colour=discord.Colour.orange()))
        return 1

    if type(length) == int:
        length = (length,)

    if len(self.mess) not in length:
        await self.message.channel.send(
            embed=discord.Embed(title=f'ERROR!', description=f'> **Usage:** ***{help_content}***!',
                                colour=discord.Colour.red()))
        return 1
    return 0


class AdminCommends:
    __doc__ = 'All admin commends HAVE TO be in this class!!! All MemberCommends are also AdminCommends!'

    def __init__(self, client: discord.Client, message: discord.Message):
        self.client, self.message, self.mess = client, message, message.content.split(' ')
        self.config_gn = json.load(open('../../config.json'))['general']

    async def help(self):
        content = '**╔══════──────**\n'

        for commend in AdminCommends.__dict__:
            if '__' not in commend:
                content += f'**║ ⋄ $**`{commend}`\n'
        for commend in MemberCommends.__dict__:
            if '__' not in commend and commend not in AdminCommends.__dict__.keys():
                content += f'**║ ⋄ $**`{commend}`\n'

        content += '**╚══════──────**\n'

        embed = discord.Embed(title="Adminer's commends:", description=content, colour=discord.Colour.orange())
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/icons/936263378102530088/a_d38edeebf819f73103076c56c141865b.webp')

        await self.message.channel.send(embed=embed)

    async def test_vs_stats_embed(self):
        embed = discord.Embed(title='Sniped Nitro!')
        embed.set_author(name='Velocity')
        embed.add_field(name='type', value='`Nitro Monthly`')
        embed.add_field(name='delay', value='`0.245829s`')
        embed.add_field(name='Guild', value='`0.୫ /dhc`')
        embed.add_field(name='Author', value='`linz#0007`')
        embed.add_field(name='Code', value='`BKJuANe3MKWG74hu`')
        embed.add_field(name='Token Ending', value='`bOJZ0`')
        embed.add_field(name='Sniper', value='`AFFICIATE#6168`')
        embed.set_footer(text='Velocity • Dziś o 16:30')

        await self.message.channel.send(embed=embed)

    async def start_order(self):
        payment_obj = Payment(None, None, None, None)
        await self.message.channel.send(embed=payment_obj.start_order_embed(), components=[payment_obj.start_order_button()])

    async def add_to_queue(self):
        if await check_commend_format(self, '$add_to_queue `<user_id>` `<token>` `<nitro_bought>`', 4) != 0: return

        order = Order(user_id=self.mess[1], token=self.mess[2], nitro_bought=self.mess[3])

        user_id, token, nitro_bought = order.user_id, order.token, order.nitro_bought

        if order.order_correctness_code != 0:
            await self.message.channel.send(embed=order.order_correctness_embed)
            return

        if self.config_gn['customer_role_id'] is not None:
            customer_role = self.message.guild.get_role(self.config_gn['customer_role_id'])
            await self.message.guild.get_member(user_id).add_roles(customer_role)

        success_embed = Queue.add_order(Queue(), order.data)

        start_order_again_btn = Payment.start_order_button(Payment(None, None, None, None))
        start_order_again_btn.label = 'Start another order!'

        await self.message.channel.send(embed=success_embed, components=[start_order_again_btn])

    async def delete_from_queue(self):
        if await check_commend_format(self, '$delete_from_queue `<order_id>`', 2) != 0: return

        code = Queue().delete_order(self.mess[1])
        if code == 0:
            await self.message.channel.send(
                embed=discord.Embed(title='Order has been successfully deleted!',
                                    colour=discord.Colour.green()))
            return
        else:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Invalid `<order_id>`!',
                                    colour=discord.Colour.red()))
            return

    async def change_token(self):
        if await check_commend_format(self, '$change_token `<order_id>` `<token>`', 3) != 0: return
        queue = Queue()
        data = queue.order_info(self.mess[1])

        if data == 1:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Invalid `<order_id>`!',
                                    colour=discord.Colour.red()))
            return
        else:
            checking_token = User(None, self.mess[2])

            if checking_token.token_correctness_code != 0:
                await self.message.channel.send(embed=checking_token.token_correctness_embed)
                return
            else:
                data['token'] = self.mess[2]
                queue.edit_order(self.mess[1], data)
                await self.message.channel.send(embed=discord.Embed(title='Token has been changed successfully!',
                                                                    colour=discord.Colour.green()))

    async def vs_rerun(self):
        if len(self.mess) == 2 and self.mess[1] in ['-h', '-help', '--help', 'help']:
            await self.message.channel.send(
                embed=discord.Embed(title='Usage: `$vs_rerun [optional:] <order_id>`', colour=discord.Colour.orange()))
            return

        queue = Queue()

        if len(self.mess) == 1:
            str_reruned_order_id = list(queue.data())[0]

        elif len(self.mess) == 2:
            if self.mess[1] not in list(queue.data()):
                await self.message.channel.send(
                    embed=discord.Embed(title=f'ERROR! No order: `{self.mess[1]}`!', colour=discord.Colour.red()))
                return
            str_reruned_order_id = self.mess[1]

        else:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Usage: `$vs_rerun [optional:] <order_id>`',
                                    colour=discord.Colour.red()))
            return


        queue.change_current_order_id(str_reruned_order_id)

        msg = await self.message.channel.send(
            embed=discord.Embed(title='Rerunning snipers...', colour=discord.Colour.gold()))

        await queue.safe_rerun_snipers(claimed=False)

        await msg.edit(embed=discord.Embed(title='Snipers rerunned successfully.', colour=discord.Colour.green()))

    async def vs_stop(self):
        await Queue().stop_snipers()
        await self.message.channel.send(
            embed=discord.Embed(title='Snipers stopped successfully.', colour=discord.Colour.green()))

    async def nuke(self):
        if await check_commend_format(self, '$nuke', 1) != 0: return
        for msg in await self.message.channel.history(limit=None).flatten():
            await msg.delete()

    async def price(self):
        if await check_commend_format(self, '$price `<option (-s/--set, -d/--delete)>` `<payment method>` `<price (if -s/--set)>`', (3, 4)) != 0: return
        if self.mess[1] in ('-s', '--set'):
            if await check_commend_format(self, '$price ` `<option (-s/--set)>` `<price>`', 4) != 0: return
            try:
                price = float(self.mess[3])
            except ValueError:
                await self.message.channel.send(embed=discord.Embed(title='ERROR! Invalid `<price>`!', colour=discord.Colour.red()))
                return
            code = Prices().change_prices(self.mess[2], price)
            if code == 1:
                await self.message.channel.send(
                    embed=discord.Embed(title='ERROR! Invalid `<payment method>`!', colour=discord.Colour.red()))
                return
            else:
                await self.message.channel.send(
                    embed=discord.Embed(title=f'Price for `{self.mess[2]}` has been set to `{price}`€.', colour=discord.Colour.green()))
                return

        elif self.mess[1] in ('-d', '--delete'):
            if await check_commend_format(self, '$price `<option (-d/--delete)>`', 3) != 0: return
            code = Prices().change_prices(self.mess[2], None)
            if code == 1:
                await self.message.channel.send(
                    embed=discord.Embed(title='ERROR! Invalid `<payment method>`!', colour=discord.Colour.red()))
                return
            else:
                await self.message.channel.send(
                    embed=discord.Embed(title=f'Price for `{self.mess[2]}` has been deleted.', colour=discord.Colour.green()))
                return
        else:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Invalid `<option (-s/--set, -d/--delete)>`!', colour=discord.Colour.red()))
            return

    async def add_to_ticket(self):
        if await check_commend_format(self, '$add_to_ticket `<user id/ping>`', 2) != 0: return
        ticket = self.message.channel
        user = client.get_user(int(self.mess[1].replace('<@', '').replace('>', '')))
        if user is not None:
            await ticket.set_permissions(user, send_messages=True, read_messages=True)
            await self.message.channel.send(embed=discord.Embed(title=f'Successfully added <@{user.id}>!',
                                                                colour=discord.Colour.green()))
        else:
            await self.message.channel.send(
                embed=discord.Embed(title=f'ERROR! Invalid `<user id/ping>`!',
                                    colour=discord.Colour.red()))

    async def kick_from_ticket(self):
        if await check_commend_format(self, '$add_to_ticket `<user id/ping>`', 2) != 0: return
        ticket = self.message.channel
        user = client.get_user(int(self.mess[1].replace('<@', '').replace('>', '')))
        if user is not None:
            await ticket.set_permissions(user, send_messages=False, read_messages=False)
            await self.message.channel.send(embed=discord.Embed(title=f'Successfully kicked `{user.name}`!',
                                                                colour=discord.Colour.green()))
        else:
            await self.message.channel.send(
                embed=discord.Embed(title=f'ERROR! Invalid `<user id/ping>`!',
                                    colour=discord.Colour.red()))

    async def change_all_claims(self):
        if await check_commend_format(self, '$change_all_claims `<amount>`', 2) != 0: return

        Queue().change_all_claims(amount=int(self.mess[1]))

        self.message.channel.send(embed=discord.Embed(title="All claims changed successfully!", colour=discord.Colour.green()))
        return


class MemberCommends:
    __doc__ = 'All members commends HAVE TO be in this class!!!'

    def __init__(self, client: discord.Client, message: discord.Message):
        self.client, self.message, self.mess = client, message, message.content.split(' ')
        self.config_gn = json.load(open('../../config.json'))['general']

    async def help(self):
        content = '**╔══════──────**\n'

        for commend in MemberCommends.__dict__:
            if '__' not in commend:
                content += f'**║ ⋄ $**`{commend}`\n'

        content += '**╚══════──────**\n'

        embed = discord.Embed(title="Member's commends:", description=content, colour=discord.Colour.orange())
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/icons/936263378102530088/a_d38edeebf819f73103076c56c141865b.webp')

        await self.message.channel.send(embed=embed)

    async def order_info(self):
        if await check_commend_format(self, '$order_info `<order_id>`', 2) != 0: return

        data = Queue().order_info(self.mess[1])

        if data == 1:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Invalid `<order_id>`!',
                                    colour=discord.Colour.red()))
            return
        else:
            embed = discord.Embed(title='Order info:', colour=discord.Colour.orange())
            content = str()
            for k, v in data.items():
                if k != 'token':
                    content += f'> **{k[0].upper() + k[1:]}:** `{v}`\n'
            embed.description = content
            embed.set_thumbnail(url=self.message.guild.get_member(user_id=data['user_id']).avatar_url)
            await self.message.channel.send(embed=embed)
            return

    async def check_token(self):
        if await check_commend_format(self, '$check_token `<token>`', 2) != 0: return

        user = User(None, self.mess[1])

        if user.token_correctness_code not in [0, 1]:
            await self.message.channel.send(embed=user.token_correctness_embed)
            return

        await self.message.channel.send(embed=user.embed_info)

    async def position(self):
        if await check_commend_format(self, '$position', 1) != 0: return

        q_data = Queue().data()
        positions = list()

        for order in q_data:
            if q_data[order]['user_id'] == self.message.author.id:
                positions.append(int(list(q_data).index(order)) + 1)

        if len(positions) == 0:
            await self.message.channel.send(embed=discord.Embed(title='You do not have any orders yet!',
                                                                description=
                                                                f'You can <#{Tickets().config()["open_ticket_channel_id"]}> and make new order.\n' 
                                                                f'Please make sure you are familiar with the <#{self.config_gn["faq_channel_id"]}> and <#{Prices().config()["prices_channel_id"]}>!',
                                                                colour=discord.Colour.red()))
            return
        elif len(positions) == 1:
            content = f'Your position in queue: `{positions[0]}`'
        else:
            content = f'Your positions in queue: '
            for pos in positions:
                content += '`' + str(pos) + '`; '

        await self.message.channel.send(embed=discord.Embed(title=content, colour=discord.Colour.orange()))

    async def crypto(self):
        if await check_commend_format(self, '$crypto', 1) != 0: return
        acceptable_crypto = json.load(open('../config/acceptable_crypto.json'))
        crypto_emoji = json.load(open('../../config.json'))['payments']['crypto_emojis']

        embed = discord.Embed(title='Acceptable crypto:', colour=discord.Colour.orange())

        content = str()

        for k, v in acceptable_crypto.items():
            content += f'<:{k}:{crypto_emoji[k]}> ** | {k}** ({v})\n'

        embed.description = content

        await self.message.channel.send(embed=embed)

    async def paypal(self):
        if await check_commend_format(self, '$paypal', 1) != 0: return
        pp_address = json.load(open('../../config.json'))['payments']['paypal_email']
        await self.message.channel.send(embed=discord.Embed(
            description=f'My **PayPal** mail address is: **{pp_address}** when sending any money remember about **F&F**',
            colour=discord.Colour.orange()), components=[Other().im_on_phone_button(pp_address)])

    async def wallet(self):
        if await check_commend_format(self, '$wallet `<crypto acronym/name>`', 2) != 0: return

        self.mess[1] = self.mess[1].lower()

        acceptable = json.load(open('../config/acceptable_crypto.json'))
        wallets = json.load(open('../../config.json'))['payments']['crypto_wallets']

        if self.mess[1].lower() in acceptable.values():
            self.mess[1] = self.mess[1].lower()
            name = self.mess[1][0].upper() + self.mess[1][1:]

        elif self.mess[1].upper() in acceptable.keys():
            self.mess[1] = acceptable[self.mess[1].upper()]
            name = self.mess[1][0].upper() + self.mess[1][1:]
        else:
            await self.message.channel.send(
                embed=discord.Embed(
                    title='ERROR! Invalid `<crypto acronym/name>`', colour=discord.Colour.red()))
            return

        try:
            await self.message.channel.send(
                embed=discord.Embed(
                    description=f'{name} wallet address: `{wallets[self.mess[1]]}`',
                    colour=discord.Colour.orange()))
            return
        except KeyError:
            await self.message.channel.send(
                embed=discord.Embed(
                    title=f'ERROR! There is no wallet for {self.mess[1]}', colour=discord.Colour.red()))
            return

    async def creation_date(self):
        if await check_commend_format(self, '$creation_date `<id/ping>` ', 2) != 0: return

        try:
            id_to_check = int(self.mess[1].replace('<@', '').replace('<#', '').replace('>', ''))
        except ValueError:
            await self.message.channel.send(
                embed=discord.Embed(title='ERROR! Invalid `<id/ping>`!',
                                    colour=discord.Colour.red()))
            return

        id_checking = User(id_to_check, None)

        if id_checking.user_id_on_server:
            id_format = f'Account <@{id_to_check}>'
        else:
            id_format = f'Id `{id_to_check}`'

        await self.message.channel.send(embed=discord.Embed(description=f'{id_format} has been created on '
                                                                        f'`{id_checking.creation_date}`.',
                                                            colour=discord.Colour.orange()))

    async def http_cat(self):
        if await check_commend_format(self, '$http_cat `<http_code>` ', 2) != 0: return

        embed = discord.Embed(colour=discord.Colour.orange())

        embed.set_image(url='https://http.cat/' + self.mess[1])

        await self.message.channel.send(embed=embed)
