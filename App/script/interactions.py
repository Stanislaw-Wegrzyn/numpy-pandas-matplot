import discord

from objects import *


class AdminInteractions:
    __doc__ = 'All admin interaction HAVE TO be in this class!!! All MemberInteractions are also AdminInteractions!!!'

    def __init__(self, client: discord.Client, interaction: discord_components.Interaction, special_arg: str or None):
        self.client, self.interaction, self.special_arg = client, interaction, special_arg
        self.config_gn = json.load(open('../../config.json'))['general']

    def __check_respond__(self, m):
        try:
            return m.channel.id == self.interaction.channel_id and (m.author.id == self.interaction.user.id or (
                    m.content[0] == '$' and (
                    m.author.id == self.config_gn['admin_id'] or m.author.id in self.config_gn['helpers_ids'])))
        except IndexError:
            return False

    async def open_transcription(self):
        await self.interaction.respond(type=6)
        Tickets().open_transcript(self.special_arg)


class MemberInteractions:
    __doc__ = 'All members interaction HAVE TO be in this class!!!'

    def __init__(self, client: discord.Client, interaction: discord_components.Interaction, special_arg: str or None):
        self.client, self.interaction, self.special_arg = client, interaction, special_arg
        self.config_gn = json.load(open('../../config.json'))['general']

    def __check_respond__(self, m):
        try:
            return m.channel.id == self.interaction.channel_id and (m.author.id == self.interaction.user.id or (
                    m.content[0] == '$' and (
                    m.author.id == self.config_gn['admin_id'] or m.author.id in self.config_gn['helpers_ids'])))
        except IndexError:
            return False

    async def im_on_phone(self):
        await self.interaction.respond(type=6)
        await self.interaction.disable_components()

        wallets = json.load(open('../../config.json'))['payments']['crypto_wallets']
        if self.special_arg in list(wallets):
            await self.interaction.channel.send(content=wallets[self.special_arg])
        else:
            await self.interaction.channel.send(content=self.special_arg)

    async def start_order(self):
        await self.interaction.respond(type=6)
        await self.interaction.disable_components()

        await self.interaction.channel.send(embed=discord.Embed(
            description=f'Check out <#{Prices().config()["prices_channel_id"]}> and in the message write the amount of nitro you would like to buy.',
            colour=discord.Colour.orange()))

        invalid_value = True

        while invalid_value:
            nitro_amount = await client.wait_for('message', check=self.__check_respond__)
            if nitro_amount.content[0] == '$': nitro_amount.content = nitro_amount.content[1:]
            try:
                nitro_amount = int(nitro_amount.content)
                invalid_value = False
            except ValueError:
                await self.interaction.channel.send(
                    embed=discord.Embed(description='Invalid value! Try again!\n(Value needs to be integer)',
                                        colour=discord.Colour.red()))
                pass

        dropdown_payment = Payment(None, None, None, None).dropdown()
        dropdown_payment.set_custom_id(f'payment_selecting|{nitro_amount}')
        await self.interaction.channel.send(components=[dropdown_payment])

    async def payment_selecting(self):
        payment_obj = Payment(None, None, None, None)
        dropdown_payment = payment_obj.dropdown()
        await self.interaction.respond(type=6)

        nitro_amount = int(self.special_arg)

        loading_message = await self.interaction.channel.send(
            embed=discord.Embed(title='Preparing your order... please wait...', colour=discord.Colour.gold()))

        for placehold in self.interaction.values:
            if placehold == self.interaction.values[0]:
                placehold = self.interaction.values[0]
                if placehold == 'paypal':
                    placehold = 'PayPal'
                else:
                    placehold = placehold[0].upper() + placehold[1:]

        dropdown_payment.placeholder = f'{placehold}'
        dropdown_payment.set_custom_id(self.interaction.component.custom_id)

        if self.interaction.values[0] == 'paypal':
            payment_method = 'paypal'
        else:
            payment_method = 'crypto'

        payment = Payment(method=self.interaction.values[0],
                          price_eur=Prices().get_prices()[payment_method] * nitro_amount,
                          pp_username=None, transaction_hash=None)

        await self.interaction.message.edit(
            embed=payment.chosen_payment_embed(),
            components=[dropdown_payment, [payment_obj.approve_order_button(), payment_obj.cancel_order_button()]])
        await loading_message.delete()

    async def approve_order(self):
        await self.interaction.disable_components()
        await self.interaction.respond(type=6)

        payment_obj = Payment(None, None, None, None)

        await self.interaction.channel.send(embed=discord.Embed(title='Send your discord T0k€n',
                                                                description=f'If you don’t know how to get your token visit <#{self.config_gn["how_to_get_token_channel_id"]}>!\nIf you are on phone go to <#{self.config_gn["how_to_get_token_phone_channel_id"]}>!\n\nIf you are surprised that we need your token, or you have questions about the security of your account, read the <#{self.config_gn["faq_channel_id"]}>!\n\nIf you want to cancel order write `\cancel`.',
                                                                colour=discord.Colour.orange()))

        while True:
            token = await client.wait_for('message', check=self.__check_respond__)
            token = token.content

            if token == '\\cancel':
                await self.interaction.channel.send(embed=discord.Embed(title='Order has been canceled!',
                                                                        description='The ticket will be shortly closed by staff.',
                                                                        colour=discord.Colour.green()),
                                                    components=[payment_obj.start_order_button()])
                return

            token = token.replace('"', '')

            token_checking_mess = await self.interaction.channel.send(
                embed=discord.Embed(title='Checking token...', colour=discord.Colour.gold()))

            token_checking = User(user_id=None, token=token)

            if token_checking.token_correctness_code != 0:
                if token_checking.token_correctness_code == 3:
                    token_checking.token_correctness_embed.description += \
                        '\n\nIf you are surprised that we need your token, or you have questions about the security of your account, read the <#973628828452790372>!\n\n' \
                        'If you want to cancel order write `\cancel`.'
                else:
                    token_checking.token_correctness_embed.description += '\nPlease try again!\n\nIf you want to cancel order write `\cancel`.'
                    await token_checking_mess.edit(embed=token_checking.token_correctness_embed)

            elif token_checking.token_correctness_code == 0:
                await token_checking_mess.edit(
                    embed=discord.Embed(title='Token approved!', colour=discord.Colour.green()))
                break

        embed_dict = self.interaction.message.embeds[0].to_dict()
        embed_waiting_for_payment, info = payment_obj.waiting_for_payment_embed(dict(embed_dict))
        await self.interaction.channel.send(embed=embed_waiting_for_payment,
                                            components=[Other().im_on_phone_button(info)])

        payment_method = self.interaction.message.embeds[0].to_dict()['title'].split(' ')[2].lower()

        # CHECKING PAYMENT FOR CRYPTO
        if payment_method != 'paypal':
            await self.interaction.channel.send(embed=discord.Embed(
                description='Send your transaction hash (transaction ID).\n\nIf you want to cancel order write `\cancel`.',
                colour=discord.Colour.orange()))

            while True:
                transaction_hash_msg = await client.wait_for('message', check=self.__check_respond__)
                transaction_hash = transaction_hash_msg.content

                checking_transaction_msg = await self.interaction.channel.send(
                    embed=discord.Embed(description=f'Checking transaction `{transaction_hash}`...`',
                                        colour=discord.Colour.orange()))

                if transaction_hash == '$lol_sudo' and (
                        transaction_hash_msg.author.id == self.config_gn['admin_id'] or transaction_hash_msg in
                        self.config_gn['helpers_ids']):
                    transaction_status_code = 0
                elif transaction_hash == '\\cancel':
                    await checking_transaction_msg.edit(
                        embed=discord.Embed(title='Order has been canceled!',
                                            description='The ticket will be shortly closed by staff.',
                                            colour=discord.Colour.green()),
                        components=[payment_obj.start_order_button()])
                    return
                else:
                    if str(self.interaction.channel.id) in list(payment_obj.get_waiting_for_supplement()):
                        price_eur = payment_obj.get_waiting_for_supplement()[str(self.interaction.channel.id)]
                    else:
                        price_eur = float(
                            self.interaction.message.embeds[0].to_dict()['fields'][1]['value'].replace('`', '').replace(
                                '€', ''))

                    payment = Payment(method=payment_method, price_eur=price_eur, pp_username=None,
                                                      transaction_hash=transaction_hash)

                    transaction_status_code = payment.check_payment()

                # REPLYING TO TRANSACTION HASH
                if transaction_status_code == 4:
                    await checking_transaction_msg.edit(
                        embed=discord.Embed(title='This transaction hash has been already used!',
                                            description='Please try again!\n\nIf you want to cancel order write `\cancel`.',
                                            colour=discord.Colour.red()))
                elif transaction_status_code == 1:
                    await checking_transaction_msg.edit(embed=discord.Embed(title='Invalid transaction hash!',
                                                                            description='Please try again!\n\nIf you want to cancel order write `\cancel`.',
                                                                            colour=discord.Colour.red()))
                elif transaction_status_code == -1:
                    await checking_transaction_msg.edit(embed=discord.Embed(title='Invalid payment method!',
                                                                            description='Please cancel your order and try another payment method!\n\nIf you want to cancel order write `\cancel`.',
                                                                            colour=discord.Colour.red()))
                elif transaction_status_code == 2:
                    await checking_transaction_msg.edit(embed=discord.Embed(title='Money sent to wrong recipient!',
                                                                            description='We are very sorry, but you sent money to wrong wallet recipient! Please try again!\n\nIf you want to cancel order write `\cancel`.',
                                                                            colour=discord.Colour.red()))
                elif type(transaction_status_code) == tuple:
                    await checking_transaction_msg.edit(embed=discord.Embed(title='Not enough money has been sent!',
                                                                            description=f'You haven’t sent enough money to our wallet (You sent {transaction_status_code[1]}€ and you should send {price_eur}€)!\n'
                                                                                        f'Don’t worry you can resend what’s missing just send your hash off transaction from which you are sending the money and don’t close the ticket'
                                                                                        f'(Our system is based on a tickets so if you close the ticket you will lose your money!)\n\n'
                                                                                        f'If you want to cancel order write `\cancel`.',
                                                                            colour=discord.Colour.red()))

                    payment.add_used_hash_id(transaction_hash)

                    payment_obj.add_waiting_for_supplement(self.interaction.channel.id, transaction_status_code[1],
                                                           price_eur)

                elif transaction_status_code == 0:
                    await checking_transaction_msg.edit(
                        embed=discord.Embed(title='Adding to queue...', colour=discord.Colour.gold()))
                    complete_message = checking_transaction_msg
                    if transaction_hash != 'lol_sudo':
                        payment.add_used_hash_id(transaction_hash)

                    payment_obj.del_waiting_for_supplement(self.interaction.channel.id)

                    break
                else:
                    await checking_transaction_msg.edit(
                        embed=discord.Embed(title=f'ERROR! {transaction_status_code}', colour=discord.Colour.red()))
                    return

        # CHECKING PAYMENT FOR PAYPAL
        else:
            await self.interaction.channel.send(embed=discord.Embed(
                description='**After sending the money send screenshot from paypal and ping wx to be added to queue.\nIt can take up to 24 hours as mentioned in <#1040927978877616138>\nPinging more than once is not gonna speed anything up just wait**',
                            colour=discord.Colour.orange()))
            """
            while True:
                message = await client.wait_for('message', check=self.__check_respond__)
                paypal_user_name = message.content
                checking_transaction_msg = await self.interaction.channel.send(
                    embed=discord.Embed(description=f'Checking payment from `{paypal_user_name}` user...`',
                                        colour=discord.Colour.orange()))
                if message.content == 'lol_sudo' and (
                        message.author.id == self.config_gn['admin_id'] or int(message.author.id) in self.config_gn[
                    'helpers_ids']):
                    transaction_status_code = 0
                elif message.content == '\\cancel':
                    await checking_transaction_msg.edit(
                        embed=discord.Embed(title='Order has been canceled!',
                                            description='The ticket will be shortly closed by staff.',
                                            colour=discord.Colour.green()),
                        components=[payment_obj.start_order_button()])
                    return
                else:
                    time.sleep(5)

                    if str(self.interaction.channel.id) in list(payment_obj.get_waiting_for_supplement()):
                        price_eur = payment_obj.get_waiting_for_supplement()[str(self.interaction.channel.id)]

                    else:
                        price_eur = float(
                            self.interaction.message.embeds[0].to_dict()['fields'][1]['value'].replace('`', '').replace(
                                '€', ''))

                    payment = Payment(method='paypal', price_eur=price_eur,
                                      pp_username=paypal_user_name,
                                      transaction_hash=None)

                    transaction_status_code = payment.check_payment()

                    if transaction_status_code in [1, 2]:
                        await checking_transaction_msg.edit(
                            embed=discord.Embed(title='No transaction found!',
                                                description='There is no new transaction from you!\n'
                                                            'Please try again!\n**(Keep in mind it has to be your username not your mail! You can find your username in settings of your paypal in section "Profile")**\n'
                                                            'If 30 minutes will pass and the bot still won’t be able to find your message open support ticket and make sure to ping xw!\n\n'
                                                            'If you want to cancel order write `\cancel`.',
                                                colour=discord.Colour.red()))

                    elif type(transaction_status_code) == tuple and transaction_status_code[0] == 3:
                        await checking_transaction_msg.edit(embed=discord.Embed(title='Not enough money has been sent!',
                                                                                description=f'You haven’t sent enough money to our paypal account (You sent {format(transaction_status_code[1], ".2f")}€ and you should send {price_eur}€)!\n'
                                                                                            f'Don’t worry you can resend what’s missing just send your paypal username from which you are sending the money and don’t close the ticket\n'
                                                                                            '(Our system is based on a tickets so if you close the ticket you will lose your money!)\n\n'
                                                                                            f'If you want to cancel order write `\cancel`.',
                                                                                colour=discord.Colour.red()))

                        payment.add_used_hash_id(transaction_status_code[1])

                    elif type(transaction_status_code) == tuple and transaction_status_code[0] == 0:
                        await checking_transaction_msg.edit(
                            embed=discord.Embed(title='Adding to queue...', colour=discord.Colour.gold()))
                        complete_message = checking_transaction_msg

                        if transaction_status_code[1] != 'lol_sudo':
                            payment.add_used_hash_id(transaction_status_code[1])
                        payment_obj.del_waiting_for_supplement(self.interaction.channel.id)
                        break
                    else:
                        await checking_transaction_msg.edit(
                            embed=discord.Embed(title=f'ERROR! {transaction_status_code}', colour=discord.Colour.red()))
                        return
                        """
        nitro_bought = int(float(self.interaction.message.embeds[0].to_dict()['fields'][0]['value'].replace('`', '')))

        order = Order(self.interaction.user.id, token, nitro_bought).data

        await complete_message.edit(embed=Queue().add_order(order))

        if self.config_gn['customer_role_id'] is not None:
            customer_role = self.interaction.message.guild.get_role(self.config_gn['customer_role_id'])
            await self.interaction.message.guild.get_member(self.interaction.user.id).add_roles(customer_role)


    async def cancel_order(self):
        await self.interaction.respond(type=6)
        await self.interaction.disable_components()
        await self.interaction.channel.send(embed=discord.Embed(title='Order has been canceled!',
                                                                description='The ticket will be shortly closed by staff.',
                                                                colour=discord.Colour.green()),
                                            components=[Payment(None, None, None, None).start_order_button()])

    async def open_ticket(self):
        value = self.interaction.values[0]
        name = value.replace('_', ' ')
        name = name[0].upper() + name[1:]

        categories = json.load(open('../config/tickets_categories_id.json'))
        category = client.get_channel(categories[value])
        everyone_role = (client.get_guild(self.config_gn['guild_id']).get_role(self.config_gn['@everyone_role_id']))

        ticket = await category.create_text_channel(name=f'ticket-{self.interaction.user.name}')

        await ticket.set_permissions(everyone_role, send_messages=False, read_messages=False)
        await ticket.set_permissions(self.interaction.user, send_messages=True, read_messages=True)

        await self.interaction.respond(type=4, content=f'Enjoy your ticket: <#{ticket.id}>')

        components = [Tickets().close_ticket_button()]

        await ticket.send(embed=discord.Embed(
            title=f'Welcome in `{name}` ticket!',
            colour=discord.Colour.orange()
        ),
            components=[components]
        )
        if category.id == Tickets().categories_ids()['buy_nitro']:
            payment_obj = Payment(None, None, None, None)
            await ticket.send(embed=payment_obj.start_order_embed(),
                              components=[payment_obj.start_order_button()])

    async def close_ticket(self):
        await self.interaction.respond(type=4, embed=discord.Embed(title='Are you sure?',
                                                                   description='Are you sure you want to close this ticket?\n'
                                                                               'To approve click button below.',
                                                                   colour=discord.Colour.orange()),
                                       components=[Tickets().approve_closing_ticket_button()])
        await self.interaction.disable_components()

    async def approve_closing_ticket(self):
        await self.interaction.respond(type=6)
        await self.interaction.disable_components()
        """
        tickets = Tickets()
        index, _, file = await tickets.save_transcript(self.interaction.channel)
        await client.get_channel(Tickets().config()['transcription_channel_id']).send(
            embed=tickets.embed_transcription(self.interaction))
        await client.get_channel(Tickets().config()['transcription_channel_id']).send(file=file)
        """
        await self.interaction.channel.delete()
