from imports import *

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


class Queue:
    def __init__(self):
        self.init_queue.start()

    @tasks.loop(count=1)
    async def init_queue(self):
        config = self.config()

        queue_channel_history = await client.get_channel(config['queue_channel_id']).history(limit=1).flatten()

        if len(queue_channel_history) == 0:
            await client.get_channel(config['queue_channel_id']).send(embed=self.embed_msg())
        else:
            try:
                try:
                    await queue_channel_history[0].edit(embed=self.embed_msg())
                except discord.errors.NotFound:
                    return
            except discord.errors.HTTPException:
                await queue_channel_history[0].delete()
                await client.get_channel(config['queue_channel_id']).send(embed=self.embed_msg())

    def data(self):
        queue = json.load(open('../config/queue.json'))
        return queue

    def config(self):
        config = json.load(open('../../config.json'))
        queue_config = config['queue']
        queue_config.update({'admin_id': config['general']['admin_id']})

        return queue_config

    def current_order_id(self):
        return open('../config/current_order_id.queue').read()

    def add_one_all_claims(self):
        all_claims = int(open('../config/all_claims.velocitysnipers').read())

        f = open('../config/all_claims.velocitysnipers', 'w')
        f.write(str(all_claims + 1))
        f.close()

        return 0

    def change_all_claims(self, amount: int):
        all_claims = int(open('../config/all_claims.velocitysnipers').read())

        f = open('../config/all_claims.velocitysnipers', 'w')
        f.write(str(amount))
        f.close()

        return 0

    def change_current_order_id(self, new_current_order_id):
        f = open('../config/current_order_id.queue', 'w')
        f.write(new_current_order_id)
        f.close()

    def overwrite(self, queue: dict):
        with open('../config/queue.json', "w") as output_db:
            output_db.write(json.dumps(queue, indent=len(queue)))
            output_db.close()

    def add_order(self, order: dict):
        queue = self.data()

        found = False
        for order_id in queue:
            if order['user_id'] == queue[str(order_id)]['user_id'] and order['token'] == queue[str(order_id)]['token']:
                found = True
                double_order_id = order_id
                break

        if found:
            queue[double_order_id]['nitro_bought'] += order['nitro_bought']

            # Increased successfully

            self.overwrite(queue)

            embed = discord.Embed(title=f'Order increased successfully!',
                                  description=f'Your order id: `{double_order_id}`.\n'
                                              'This id will be necessary in case there will be any inconveniences with your order, so keep it safe!',
                                  color=discord.Colour.green())

            embed.set_author(name=f'Thank you for using {Other().company("company_name")}!')

            return embed

        else:
            order_id = self.generate_order_id()
            order = {order_id: order}
            queue.update(order)

            # Successfully added

            self.overwrite(queue)

            embed = discord.Embed(title=f'Successfully added to queue!',
                                  description=f'Your order id: `{order_id}`.\n'
                                              '**Make sure to save this code somewhere on your pc or on a piece of paper, if you wont have it when something happens to your order I will not be able to help you** ',
                                  color=discord.Colour.green())

            embed.set_author(name=f'Thank you for using {Other().company("company_name")}!')

            return embed

    def delete_order(self, order_id: str):
        queue = self.data()

        try:
            del queue[order_id]
            self.overwrite(queue)
            return 0
        except KeyError:
            return 1  # there is no order with this id

    def edit_order(self, order_id: str, order: dict):
        queue = self.data()

        try:
            queue[order_id] = order
            self.overwrite(queue)
            return 0
        except KeyError:
            return 1  # there is no order with this id

    def order_info(self, order_id: str):
        try:
            return self.data()[order_id]
        except KeyError:
            return 1  # there is no order with this id

    def zero_in_queue(self):
        queue = self.data()

        for order_id in queue:
            if queue[order_id]['nitro_claimed'] == 0:
                str_next_order = order_id
                next_order = queue[order_id]
                return str_next_order, next_order
        return None

    def generate_order_id(self):
        queue = self.data()

        if len(list(queue.keys())) == 0:
            order_nr = '0'
        else:
            order_nr = str(int(list(queue.keys())[len(list(queue.keys())) - 1][0:3]) + 1)

        if len(order_nr) == 1:
            order_nr = '00' + order_nr
        elif len(order_nr) == 2:
            order_nr = '0' + order_nr

        random_nr = str(random.randint(1000000, 10000000))

        order_id = str(order_nr + random_nr)

        return order_id

    async def safe_rerun_snipers(self, claimed: bool):
        # OPENING DB:
        config = self.config()
        queue = self.data()

        if claimed:
            id_done_order = self.current_order_id()
            queue[id_done_order]['nitro_claimed'] += 1

            print(queue[id_done_order]['nitro_claimed'])

            self.overwrite(queue)

            self.add_one_all_claims()

            done_order = queue[id_done_order]

            is_0_in_queue = self.zero_in_queue()

            if is_0_in_queue is None and done_order['nitro_claimed'] != done_order['nitro_bought']:
                id_next_order = str(list(queue.keys())[0])
                next_order = queue[list(queue.keys())[0]]

            elif done_order['nitro_claimed'] >= done_order['nitro_bought']:
                embed = discord.Embed(
                    title=f'{Other().emoji("cool_emoji")}Nitrous Oxide Services{Other().emoji("cool_emoji")}',
                    description=
                    f'Hello there, Your order with id: {id_done_order} has been fulfilled!\n'
                    f'We hope that working with us was a pleasure.\n\n'
                    f'If you are satisfied/dissatisfied with our service, please leave a feedback on <#{1046438056183480403}> including screenshot from subscription tab from your settings.\n\n'
                    f'We would be grateful if you recommended us to your friends ({Other().company("discord_invite_url")}) and we hope that this is not the end of our cooperation.\n\n'
                    ,
                    colour=discord.Colour.green())

                embed.set_thumbnail(
                    url=Other().company('company_logo_url'))

                if client.get_user(done_order['user_id']) is not None:
                    try:
                        done_order_dm = await client.get_user(done_order['user_id']).create_dm()
                        await done_order_dm.send(embed=embed)
                    except discord.errors.Forbidden:
                        pass

                if is_0_in_queue is None:
                    if len(list(queue.keys())) == 1:
                        del queue[id_done_order]
                        self.overwrite(queue)

                        dm = await client.get_user(config['admin_id']).create_dm()
                        await dm.send(embed=discord.Embed(title='ALERT! Queue is empty!!',
                                                          description='There are no more orders in the queue.\n'
                                                                      f'Add them using the `$add_to_queue` command!',
                                                          color=discord.Colour.red()))
                        for host in config['host']:
                            stop_sniper(host, config['hosts_username'], config['hosts_password'])
                        return
                    else:
                        if list(queue.keys()).index(id_done_order) == 0:
                            id_next_order = str(list(queue.keys())[1])
                            next_order = queue[list(queue.keys())[1]]
                        else:
                            id_next_order = str(list(queue.keys())[0])
                            next_order = queue[list(queue.keys())[0]]

                        del queue[id_done_order]

                        self.overwrite(queue)
                else:
                    id_next_order = is_0_in_queue[0]
                    next_order = is_0_in_queue[1]
                    del queue[id_done_order]

                    self.overwrite(queue)

            elif is_0_in_queue is not None:
                id_next_order = is_0_in_queue[0]
                next_order = is_0_in_queue[1]
        else:

            is_0_in_queue = self.zero_in_queue()

            if is_0_in_queue is None:
                id_next_order = str(list(queue.keys())[0])
                next_order = queue[list(queue.keys())[0]]
            else:
                id_next_order = is_0_in_queue[0]
                next_order = is_0_in_queue[1]

        self.change_current_order_id(id_next_order)

        next_user = User(user_id=next_order['user_id'], token=next_order['token'])

        if next_user.token_correctness_code != 0:
            embed = discord.Embed(title='ERROR! Your token is invalid!',
                                  description=f'Sorry, but the token you gave us is invalid and breaks the <#{1046438106229919774}>.\n\n'
                                              f'**Reason: **{next_user.token_correctness_embed.description}\n\n'
                                              f'If you want to make new order, please <#{1046438206683488287}>',
                                  color=discord.Colour.red())

            embed.set_thumbnail(
                url=Other().company('company_logo_url'))

            dm = await client.get_user(next_user.id).create_dm()
            # await dm.send(embed=embed)

            if client.get_user(next_user.id) is not None:
                try:
                    done_order_dm = await client.get_user(next_user.id).create_dm()
                    await done_order_dm.send(embed=embed)
                except discord.errors.Forbidden:
                    pass

            del queue[id_next_order]

            self.overwrite(queue)

            await self.safe_rerun_snipers(claimed=False)
            return

        for host in config['hosts']:
            print(host)
            rerun_sniper(host, config['hosts_username'], config['hosts_password'], next_order['token'])

    async def stop_snipers(self):
        config = self.config()
        for host in config['hosts']:
            stop_sniper(host, config['hosts_username'], config['host_password'])

    def embed_msg(self):
        content = str()
        queue = self.data()

        ppl_counter = 0
        left_in_queue = 0

        now_sniping_person_line_hidden = ""

        for order_id, order in queue.items():
            if ppl_counter >= 50:
                if self.current_order_id() == str(order_id):
                    if client.get_user(order['user_id']) is None:
                        user_name = order['user']
                    else:
                        user_name = str(client.get_user(order['user_id']))

                    now_sniping_person_line_hidden = user_name + '| `' + str(order['nitro_claimed']) + '`/`' + str(
                        order['nitro_bought']) + f'` {Other().emoji("current_order_emoji")}'
                left_in_queue += 1
            else:
                if client.get_user(order['user_id']) is None:
                    user_name = order['user']
                else:
                    user_name = str(client.get_user(order['user_id']))

                if self.current_order_id() == str(order_id):
                    now_sniping_person_line = user_name + '| `' + str(order['nitro_claimed']) + '`/`' + str(
                        order['nitro_bought']) + f'` {Other().emoji("current_order_emoji")}'
                    content += now_sniping_person_line + '\n'
                else:
                    content += user_name + '| `' + str(order['nitro_claimed']) + '`/`' + str(
                        order['nitro_bought']) + f'` {Other().emoji("waiting_order_emoji_odj")}\n'
            ppl_counter += 1

        if left_in_queue > 0:
            content += f"\n({left_in_queue} more people in queue)\n"
        if now_sniping_person_line_hidden != "":
            content += f"{now_sniping_person_line_hidden}\n"

        embed = discord.Embed(title='Queue: ', description=f'{content}', colour=discord.Colour.orange())

        return embed


class User:
    def __init__(self, user_id: int or None, token: str or None):
        self.token = token
        self.id = user_id
        self.headers = {'Authorization': self.token, 'Content-type': 'application/json'}
        self.api = 'https://discord.com/api/v9/users/@me'

        self.info = dict()
        self.nitro_info = {'Actual Nitro': '', 'Nitro Monthly': 0, 'Nitro Basic Monthly': 0}

        if self.id is not None:
            # ID CREATION DATE (in js)
            var = Scope(JS_BUILTINS)
            set_global_object(var)

            var.registers(['m', 'unix', 'unixbin', 'bin'])
            var.put('id', Js(str(self.id)))
            var.put('bin', (+var.get('id')).callprop('toString', Js(2.0)))
            var.put('unixbin', Js(''))
            var.put('unix', Js(''))
            var.put('m', (Js(64.0) - var.get('bin').get('length')))
            var.put('unixbin', var.get('bin').callprop('substring', Js(0.0), (Js(42.0) - var.get('m'))))
            var.put('unix', (var.get('parseInt')(var.get('unixbin'), Js(2.0)) + Js(1420070400000.0)))
            unix = var.get('unix')
            pass

            unix_float = str(str(unix)[:11] + '.' + str(unix)[11:])[1:15]

            self.creation_date = datetime.fromtimestamp(float(unix_float))

            # IS USER_ID ON SERVER?
            if client.get_user(self.id) is None:
                self.user_id_on_server = False
            else:
                self.user_id_on_server = True
        else:
            self.creation_date = None
            self.user_id_on_server = None

        if self.token is None:
            self.token_correctness_code = -1

        # TOKEN CORRECTNESS
        if type(token) == str:
            if len(self.token.split('.')) != 3 or len(self.token) < 59:
                self.token_correctness_code = 4  # invalid token format
                self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                             description='Invalid Token format!',
                                                             colour=discord.Colour.red())
            elif token[0:4] == 'mfa.':
                self.token_correctness_code = 3  # invalid token format (2fa)
                self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                             description='Token have enabled 2fa!',
                                                             colour=discord.Colour.red())
            else:
                with requests.request('GET', self.api, headers=self.headers) as response:
                    api_data = response.json()
                    if str(api_data) == "{'message': '401: Unauthorized', 'code': 0}":
                        self.token_correctness_code = 2  # invalid token
                        self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                                     description='Token does not exist!',
                                                                     colour=discord.Colour.red())
                    elif api_data['phone'] is None:
                        self.token_correctness_code = 1  # no phone token
                        self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                                     description='Token is not verified by phone number!',
                                                                     colour=discord.Colour.red())
                    elif api_data['email'] is None:
                        self.token_correctness_code = 5  # no email
                        self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                                     description='Token is not email!',
                                                                     colour=discord.Colour.red())
                    elif api_data['verified'] == False:
                        self.token_correctness_code = 6  # no email verified
                        self.token_correctness_embed = discord.Embed(title='Invalid Token!',
                                                                     description='Email in token is not verified!',
                                                                     colour=discord.Colour.red())
                    else:
                        self.token_correctness_code = 0
                        print(api_data['verified'])
                        print(type(api_data['verified']))
                        self.token_correctness_embed = discord.Embed(title='Token correct!',
                                                                     colour=discord.Colour.green())

        if self.token_correctness_code == 0:

            # NUMBER OF GUILDS
            self.guilds_number = len(requests.request('GET', self.api + '/guilds', headers=self.headers).json())

            # GENERAL TOKEN INFORMATION
            response = requests.request('GET', self.api, headers=self.headers)
            for info_name, info in dict(response.json()).items():
                if info_name in (
                'username', 'discriminator', 'id', 'locale', 'email', 'verified', 'phone', 'bio', 'avatar'):
                    if len(str(info)) == 0: info = 'None'
                    self.info.update({info_name: str(info)})
            self.info.update({'number of guilds': self.guilds_number})
            self.avatar_png = f'https://cdn.discordapp.com/avatars/{self.info["id"]}/{self.info["avatar"]}.png'

            # NITRO INFORMATION
            response = requests.request('GET',
                                        self.api + '/applications/521842831262875670/entitlements?exclude_consumed=true',
                                        headers=self.headers)
            for subscription in response.json():
                try:
                    self.nitro_info[subscription['subscription_plan']['name']] += 1
                    actual_premium_nr = requests.request('GET', self.api, headers=self.headers).json()['premium_type']
                    if actual_premium_nr == 2:
                        actual_premium = "Nitro Boost"
                    elif actual_premium_nr == 1:
                        actual_premium = "Nitro Basic"
                    elif actual_premium_nr == 0:
                        actual_premium = "None"
                    self.nitro_info[
                        'Actual Nitro'] = actual_premium  # TODO: ĹĽle pokazuje i trzeba by wgl sprawdziÄ‡ o co chodzi
                except KeyError:
                    self.nitro_info['Actual Nitro'] = 'None'

            # THIS USER'S TOKEN?
            if self.id is not None:
                if self.id == self.info["id"]:
                    self.token_equal_user = True
                else:
                    self.token_equal_user = False
            else:
                self.token_equal_user = None

            # TOKEN CREATION DATE (in js)
            var = Scope(JS_BUILTINS)
            set_global_object(var)

            var.registers(['m', 'unix', 'unixbin', 'bin'])
            var.put('id', Js(str(self.info["id"])))
            var.put('bin', (+var.get('id')).callprop('toString', Js(2.0)))
            var.put('unixbin', Js(''))
            var.put('unix', Js(''))
            var.put('m', (Js(64.0) - var.get('bin').get('length')))
            var.put('unixbin', var.get('bin').callprop('substring', Js(0.0), (Js(42.0) - var.get('m'))))
            var.put('unix', (var.get('parseInt')(var.get('unixbin'), Js(2.0)) + Js(1420070400000.0)))
            unix = var.get('unix')
            pass

            unix_float = str(str(unix)[:11] + '.' + str(unix)[11:])[1:15]

            self.token_creation_date = datetime.fromtimestamp(float(unix_float))

            # CREATING EMBED WITH USER INFO
            content = str()

            if self.token_equal_user in [True, None]:
                for info_name, info in self.info.items():
                    content += f'| **{info_name[0].upper() + info_name[1:]}:** `{str(info)}`\n'
                content += f'| **Creation date:** `{str(self.token_creation_date)}`\n'
                content += '\n'
                for nitro_type, nitro in self.nitro_info.items():
                    content += f'| **{nitro_type}:** `{nitro}\n`'

                embed_info_pattern = discord.Embed(title=self.info['username'] + '#' + self.info['discriminator'],
                                                   description=content,
                                                   colour=discord.Colour.orange())
                embed_info_pattern.set_thumbnail(url=self.avatar_png)

                self.embed_info = embed_info_pattern
            else:
                content += '**User Id Info**:\n' \
                           f' **|** On server: `{self.user_id_on_server}`\n'
                if self.user_id_on_server:
                    content += f' **|** User name: `{str(client.get_user(self.id))}`\n'

                content += f'| **Id creation date:** `{str(self.creation_date)}`\n'

                content += '\n\n**Token Info**:\n'

                for info_name, info in self.info.items():
                    content += f'| **{info_name[0].upper() + info_name[1:]}:** `{str(info)}`\n'
                content += f'| **Token creation date:** `{str(self.token_creation_date)}`\n'
                content += '\n'
                for nitro_type, nitro in self.nitro_info.items():
                    content += f'| **{nitro_type}:** `{nitro}\n`'

                embed_info_pattern = discord.Embed(
                    title=str(client.get_user(self.id)) + ' or ' + self.info['username'] + '#' + self.info[
                        'discriminator'],
                    description=content,
                    colour=discord.Colour.orange())
                embed_info_pattern.set_thumbnail(url=self.avatar_png)

                self.embed_info = embed_info_pattern

    def id_position_is_queue(self, queue: dict):
        positions = list()
        for order_id, order in queue.items():
            if order['user_id'] == self.id:
                positions.append(int(list(queue).index(order_id)) + 1)

        if len(positions) == 0:
            return None
        else:
            return positions

    def id_in_queue(self, queue: dict):
        for order_id, order in queue.items():
            if order['user_id'] == self.id:
                return True
        return False

    def token_position_is_queue(self, queue: dict):
        positions = list()
        for order_id, order in queue.items():
            if order['token'] == self.token:
                positions.append(int(list(queue).index(order_id)) + 1)

        if len(positions) == 0:
            return None
        else:
            return positions

    def token_in_queue(self, queue: dict):
        for order_id, order in queue.items():
            if order['token'] == self.token:
                return True
        return False

    def user_in_queue(self, queue: dict):
        for order_id, order in queue.items():
            if order['user_id'] == self.id and order['token'] == self.token:
                return True
        return False

    def orders_ids(self, queue):
        orders_ids = list()
        for order_id, order in queue.items():
            if order['user_id'] == self.id and self.token:
                orders_ids.append(order_id)
        if len(orders_ids) == 0:
            return None
        else:
            return orders_ids


class Order:
    def __init__(self, user_id: int, token: str, nitro_bought: int):
        self.user_id = user_id
        self.token = token
        self.nitro_bought = nitro_bought

        if None in [user_id, token, nitro_bought]: return

        try:
            self.nitro_bought = int(self.nitro_bought)
        except ValueError:
            self.order_correctness_code = 6  # invalid nitro_bought format (not int)
            self.order_correctness_embed = discord.Embed(title='Invalid nitro_bought format!',
                                                         description='Value has to be integer!',
                                                         colour=discord.Colour.red())
            return

        try:
            self.user_id = int(self.user_id)
        except ValueError:
            self.order_correctness_code = 5  # invalid nitro_bought format (not int)
            self.order_correctness_embed = discord.Embed(title='Invalid user_id format!',
                                                         description='Value has to be integer!',
                                                         colour=discord.Colour.red())
            return

        order_user = User(user_id=self.user_id, token=self.token)

        # CHECKING CORRECTNESS OF ARGS IN ORDER
        if self.nitro_bought < 1:
            self.order_correctness_code = 4  # invalid nitro_bought format (too low value)
            self.order_correctness_embed = discord.Embed(title='Invalid nitro_bought format!',
                                                         description='You need to chose at least 1 nitro!',
                                                         colour=discord.Colour.red())
        elif self.nitro_bought > 100:
            self.order_correctness_code = 3  # invalid nitro_bought format
            self.order_correctness_embed = discord.Embed(title='Invalid nitro_bought format!',
                                                         description='Max value for nitro is `100`!',
                                                         colour=discord.Colour.red())
        elif order_user.token_correctness_code != 0:
            self.order_correctness_code = 2  # invalid token format
            self.order_correctness_embed = order_user.token_correctness_embed
        elif not order_user.user_id_on_server:
            self.order_correctness_code = 1  # there is no user with this id
            self.order_correctness_embed = discord.Embed(title='Invalid user id!',
                                                         description=f'There is no user with this id: `{self.user_id}`',
                                                         colour=discord.Colour.red())
        else:
            self.order_correctness_code = 0
            order = dict()
            order.update({'user': str(client.get_user(self.user_id))})
            order.update({'user_id': self.user_id})
            order.update({'token': self.token})
            order.update({'nitro_bought': self.nitro_bought})
            order.update({'nitro_claimed': 0})
            self.data = order


class Payment:
    def __init__(self, method: str or None, price_eur: float or None,
                 pp_username: str or None, transaction_hash: str or None):
        self.method, self.price_eur, self.pp_username, self.transaction_hash = \
            method, price_eur, pp_username, transaction_hash

    def config(self):
        config = json.load(open('../../config.json'))
        config_out = config['payments']
        config_out.update({'prices_emoji': config['prices']['prices_emoji']})
        return config_out

    def get_waiting_for_supplement(self):
        waiting_for_supplement = json.load(open('../config/waiting_for_supplement.json'))
        return waiting_for_supplement

    def add_waiting_for_supplement(self, channel_id: int, price_sent: float, price_require: float):
        waiting_for_supplement = self.get_waiting_for_supplement()
        if str(channel_id) in list(waiting_for_supplement):
            waiting_for_supplement[str(channel_id)] = price_sent - price_require
        else:
            waiting_for_supplement.update({str(channel_id): price_sent - price_require})

        with open('../config/waiting_for_supplement.json', "w") as output_db:
            output_db.write(json.dumps(waiting_for_supplement, indent=len(waiting_for_supplement)))
            output_db.close()

    def del_waiting_for_supplement(self, channel_id: int):
        waiting_for_supplement = self.get_waiting_for_supplement()
        try:
            del waiting_for_supplement[str(channel_id)]

            with open('../config/waiting_for_supplement.json', "w") as output_db:
                output_db.write(json.dumps(waiting_for_supplement, indent=len(waiting_for_supplement)))
                output_db.close()
            return 0
        except KeyError:
            return 1

    def used_hashes_ids(self):
        hashes_ids_used = json.load(open('../config/used_hashes_ids.json'))
        used_hashes = hashes_ids_used[self.method.lower()]
        return used_hashes

    def add_used_hash_id(self, hash_id: str):
        hashes_ids_used = json.load(open('../config/used_hashes_ids.json'))
        hashes_ids_used[self.method.lower()].append(hash_id)
        with open('../config/used_hashes_ids.json', "w") as output_db:
            output_db.write(json.dumps(hashes_ids_used, indent=len(hashes_ids_used)))
            output_db.close()
        return 0

    def usd_to_eur(self, usd_value: float):
        google_finance_url = f'https://www.google.com/finance/quote/USD-EUR'
        try:
            eur_value = float(
                requests.get(google_finance_url).text.split('<div class="YMlKec fxKbKc">')[1].split('</div>')[
                    0].replace(',', '.'))
        except IndexError:
            time.sleep(0.3)
            eur_value = float(
                requests.get(google_finance_url).text.split('<div class="YMlKec fxKbKc">')[1].split('</div>')[
                    0].replace(',', '.'))

        eur_value = eur_value * usd_value

        return eur_value

    def check_payment(self):
        print(self.method, self.config()['crypto_wallets'].keys())
        if self.method not in self.config()['crypto_wallets'].keys() and self.method != 'paypal':
            return -1  # invalid payment method
        elif self.pp_username is None and None not in [self.transaction_hash, self.price_eur, self.method]:
            crypto_wallets = self.config()['crypto_wallets']
            used_hashes = self.used_hashes_ids()

            crypto_name = self.method.lower()

            block_chain_api_url = f"https://api.blockchair.com/{crypto_name.replace(' ', '-')}/dashboards/transaction/{self.transaction_hash}"

            transaction = requests.request(method='GET', url=block_chain_api_url)

            if transaction.status_code == 404 or len(transaction.json()['data']) == 0:
                return 1  # invalid self.transaction_hash

            transaction = transaction.json()
            try:
                for output in transaction["data"][self.transaction_hash]["outputs"]:
                    output_usd = output["value_usd"]
                    recipient = output["recipient"]

                    output_eur = self.usd_to_eur(output_usd)

                    if recipient.lower() == crypto_wallets[crypto_name].lower():
                        if self.transaction_hash in used_hashes:
                            return 4  # nice try id already used
                        elif output_eur < self.price_eur - .15:
                            self.add_used_hash_id(self.transaction_hash)
                            return 3, output_eur  # not enough money sent
                        self.add_used_hash_id(self.transaction_hash)
                        return 0  # everything is fine
                return 2  # money sent to wrong recipient

            except KeyError:
                for output in transaction["data"][self.transaction_hash]["calls"]:
                    output_usd = output["value_usd"]
                    recipient = output["recipient"]

                    output_eur = self.usd_to_eur(output_usd)

                    if recipient.lower() == crypto_wallets[crypto_name].lower():
                        if self.transaction_hash in used_hashes:
                            return 4  # nice try id already used
                        elif output_eur < self.price_eur - .15:
                            self.add_used_hash_id(self.transaction_hash)
                            return 3, output_eur  # not enough money sent
                        self.add_used_hash_id(self.transaction_hash)
                        return 0  # everything is fine
                return 2  # money sent to wrong recipient

        elif None not in [self.pp_username, self.price_eur, self.method] and None in [self.transaction_hash]:
            config = self.config()
            another_payment_method_recipients = config['another_payment_method_recipients']
            imap_info_pass = config['imap_mail_password']

            used_ids = self.used_hashes_ids()

            imap_server = config['imap_server']
            email_address = another_payment_method_recipients['paypal']

            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(email_address, imap_info_pass)
            imap.select('Inbox')

            _, msgnums = imap.search(None, 'ALL')
            list_msgnums = list(msgnums[0].split())
            list_msgnums.reverse()

            counter = 0

            for msgnum in list_msgnums:
                _, data = imap.fetch(msgnum, "(RFC822)")
                message = email.message_from_bytes(data[0][1])

                if message.get('Subject') == "You've got money":
                    content = str()
                    for part in message.walk():
                        if part.get_content_type() == 'text/html':
                            content += part.as_string()
                    content = str(content.encode()).replace('=\\n', '')

                    if ' has sent you =E2=82=AC' and '=C2=A0EUR</span></p>' in content:
                        if counter >= config['numbers_of_mails_timeout_paypal']: return 1  # invalid name
                        money_sent = float(content.split(
                            'Amount received</strong></td>=0A                                  <td align=3D"right">=E2=82=AC')[
                                               1].split('=C2=A0EUR</td>')[0].replace(',', '.'))
                        transaction_id = \
                        content.split('Transaction ID</strong></span><br /><span>')[1].split('</span></td>')[0]
                        try:
                            pp_username_mail = ""  # TODO: get user firs and last name
                            pp_username_mail.replace(' ', '')
                        except IndexError:
                            counter += 1
                        else:
                            if self.pp_username == pp_username_mail:

                                if transaction_id in used_ids:
                                    return 2  # nice try id already used
                                elif money_sent < self.price_eur:
                                    self.add_used_hash_id(transaction_id)
                                    return 3, money_sent  # not enough money
                                self.add_used_hash_id(transaction_id)
                                return 0
                            counter += 1
            return 1  # invalid transaction code

        else:
            return -666  # some invalid init for payment

    def dropdown(self):
        config = self.config()
        crypto_names = json.load(open('../config/acceptable_crypto.json'))
        crypto_emojis = config['crypto_emojis']
        prices_emojis = config['prices_emoji']
        print(crypto_names, '\n', crypto_emojis, '\n', prices_emojis)
        prices = Prices()
        prices = prices.get_prices()
        options = list()

        for method, price in prices.items():
            if price is not None and method != 'crypto':
                if method == 'paypal':
                    method = 'PayPal'
                elif method == 'paysafecard':
                    method = 'PaySafeCard'

                method = method[0].upper() + method[1:]

                if prices_emojis[method] is None:
                    emoji = None
                else:
                    emoji = discord.PartialEmoji(name=method, id=prices_emojis[method])

                options.append(
                    SelectOption(value=method.lower(), label=method, description=f'Payment by {method} service.',
                                 emoji=emoji))

        for crypto in crypto_names.keys():
            if crypto_emojis[crypto] is None:
                emoji = None
            else:
                emoji = discord.PartialEmoji(name=crypto, id=crypto_emojis[crypto])

            options.append(SelectOption(value=crypto_names[crypto].lower(),
                                        label=crypto_names[crypto][0].upper() + crypto_names[crypto][1:].lower(),
                                        description=crypto[0].upper() + crypto[1:],
                                        emoji=emoji))

        dropdown = Select(placeholder='Select your payment method:', options=options, custom_id='payment_selecting')

        return dropdown

    def start_order_button(self):
        button = Button(label='Start order!', custom_id='start_order', style=ButtonStyle.green)
        return button

    def approve_order_button(self):
        button = Button(label='Approve!', custom_id='approve_order', style=ButtonStyle.green)
        return button

    def cancel_order_button(self):
        button = Button(label='Cancel!', custom_id='cancel_order', style=ButtonStyle.red)
        return button

    def waiting_for_payment_embed(self, confirmation_embed_dict: dict):
        acceptable_crypto = json.load(open('../config/acceptable_crypto.json'))
        config_gn = json.load(open('../../config.json'))['general']
        embed = discord.Embed.from_dict(data=confirmation_embed_dict)

        payment_method = confirmation_embed_dict['title']
        payment_method = payment_method.split(' ')[2].lower()

        if payment_method == 'paypal':
            embed.add_field(name=f'{payment_method} recipient',
                            value=f'```{self.config()["paypal_email"]}```')
            embed.description = '**__REMEMBER TO SEND MONEY BY f&f NOT g&s__**' \
                                f'\nAll transaction by g&s wont be accepted **and wont be refunded (<#{config_gn["roles_channel_id"]}>)**'
            return embed, self.config()["paypal_email"]
        else:
            crypto = acceptable_crypto[
                confirmation_embed_dict['fields'][2]['name'].split(' ')[0].replace('[', '').replace(']', '')]
            wallet = Payment(None, None, None, None).config()['crypto_wallets'][crypto]
            amount = confirmation_embed_dict['fields'][2]['value'].replace('`', '').split(' ')[0]

            qr_url = f'https://chart.googleapis.com/chart?chs=500x500&chld=L|2&cht=qr&chl={crypto}:{wallet}?amount={amount}%26label=Nitrous%20Oxide%20Services%26message=Cheapest%20nitro'

            embed.add_field(name='Wallet recipient', value=f'```{wallet}```')
            embed.set_image(url=qr_url)

            return embed, wallet

    def chosen_payment_embed(self):
        cg_api = CoinGeckoAPI()
        acceptable_crypto = json.load(open('../config/acceptable_crypto.json'))

        if self.method == 'paypal':
            payment_method = 'paypal'
        else:
            payment_method = 'crypto'

        price = Prices().get_prices()[payment_method]
        selected_payment_method_name = self.method[0].upper() + self.method[1:]

        embed = discord.Embed(title=f'Payment method {selected_payment_method_name}', colour=discord.Colour.orange())
        embed.add_field(name='Nitro amount', value=f'`{str(self.price_eur / price)}`')

        embed.add_field(name='[€] Price', value=f'`{str(self.price_eur)}`€')

        if self.method != 'paypal':
            embed.add_field(
                name=f'[{list(acceptable_crypto)[list(acceptable_crypto.values()).index(self.method)]}] Price',
                value=f'`{format(((1 / cg_api.get_price(ids=self.method, vs_currencies="eur")[self.method]["eur"]) * self.price_eur), ".10f")}` {list(acceptable_crypto)[list(acceptable_crypto.values()).index(self.method)]}')
        return embed

    def start_order_embed(self):
        emded = discord.Embed(title='Hello there!',
                              description='Press the button when you are ready and enjoy your order!',
                              colour=discord.Colour.green())

        return emded


class Prices:
    def __init__(self):
        self.init_prices.start()

    @tasks.loop(count=1)
    async def init_prices(self):
        config = self.config()
        price_channel_history = await client.get_channel(config['prices_channel_id']).history(limit=1).flatten()

        if len(price_channel_history) == 0:
            await client.get_channel(config['prices_channel_id']).send(embed=self.embed_msg())
        else:
            try:
                try:
                    await price_channel_history[0].edit(embed=self.embed_msg())
                except discord.errors.NotFound:
                    return
            except discord.errors.HTTPException:
                await price_channel_history[0].delete()
                await client.get_channel(config['prices_channel_id']).send(embed=self.embed_msg())

    def config(self):
        config = json.load(open('../../config.json'))
        config = config['prices']
        return config

    def get_prices(self):
        return json.load(open('../config/prices.json'))

    def change_prices(self, method: str, price: float or None):
        try:
            prices = json.load(open('../config/prices.json'))
            prices[method.lower()] = price
            with open('../config/prices.json', "w") as output_db:
                output_db.write(json.dumps(prices, indent=len(prices)))
                output_db.close()
            return 0
        except KeyError:
            return 1  # invalid payment method

    def embed_msg(self):
        prices = self.get_prices()
        prices_emoji = self.config()['prices_emoji']

        embed = discord.Embed(title='Prices:', colour=discord.Colour.orange())

        content = str()

        for method, price in prices.items():
            if method == 'paypal':
                method = 'PayPal'
            elif method == 'paysafecard':
                method = 'PaySafeCard'

            if method == 'crypto':
                emoji = 'BTC'
            else:
                emoji = method[0].upper() + method[1:]

            if prices_emoji[emoji] is None:
                emoji = ""
            else:
                emoji = f'<:{emoji}:{prices_emoji[emoji]}>'

            if price is None:
                content += f'**{emoji} | {method[0].upper() + method[1:]}:**`not available` {Other().emoji("cool_emoji")}\n'
            else:
                content += f'**{emoji} | {method[0].upper() + method[1:]}:** `{price}`**€**/1 **claim** {Other().emoji("cool_emoji")}\n'

        embed.description = content

        return embed


class Other:
    def im_on_phone_button(self, info: str):
        button = Button(label="I'm on phone!", custom_id=f'im_on_phone|buttons are currently under maintaince',
                        style=ButtonStyle.blue, emoji="📱")
        return button

    def emoji(self, emoji_name):
        config_gn = json.load(open('../../config.json'))['general']

        try:
            return config_gn[emoji_name]
        except KeyError:
            return 1

    def company(self, item):
        config_gn = json.load(open('../../config.json'))['general']

        try:
            return config_gn[item]
        except KeyError:
            return 0


class Tickets:

    def __init__(self):
        self.init_ticket.start()

    @tasks.loop(count=1)
    async def init_ticket(self):
        config = self.config()
        ticket_channel_history = await client.get_channel(config['open_ticket_channel_id']).history(limit=1).flatten()

        if len(ticket_channel_history) == 0:
            await client.get_channel(config['open_ticket_channel_id']).send(embed=self.embed(),
                                                                            components=[self.dropdown()])
        else:
            try:
                try:
                    await ticket_channel_history[0].edit(embed=self.embed())
                except discord.errors.NotFound:
                    return
            except discord.errors.HTTPException:
                await ticket_channel_history[0].delete()
                await client.get_channel(config['open_ticket_channel_id']).send(embed=self.embed(),
                                                                                components=[self.dropdown()])

    def config(self):
        config = json.load(open('../../config.json'))
        config = config['tickets']
        return config

    def transcriptions_indexes(self):
        indexes = json.load(open('../config/transcripts_indexes.json'))
        return indexes

    def last_transcript_index(self):
        f = open('../config/index.transcript')
        counter = int(f.read())
        return counter

    def change_transcript_index(self, new_index: int):
        f = open('../config/index.transcript')
        counter = int(f.read())
        f = open('../config/index.transcript', 'w')
        f.write(str(new_index))
        f.close()
        return 0

    def categories_emojis(self):
        config = json.load(open('../config/tickets_emoji.json'))
        return config

    def categories_ids(self):
        config = json.load(open('../config/tickets_categories_id.json'))
        return config

    def categories(self):
        config = json.load(open('../config/tickets_categories.json'))
        return config

    def add_category(self, value: str, description: str, emoji: str, category_id: int):
        config = self.categories()
        emojis = self.categories_emojis()
        ids = self.categories_ids()
        if value in config.keys():
            return 1  # category already exist
        config.update({value: description})
        emojis.update({value: emoji})
        ids.update({value: category_id})
        with open('../config/tickets_categories.json', "w") as output_db:
            output_db.write(json.dumps(config, indent=len(config)))
            output_db.close()
        with open('../config/tickets_emoji.json', "w") as output_db:
            output_db.write(json.dumps(emojis, indent=len(emojis)))
            output_db.close()
        with open('../config/tickets_categories_id.json', "w") as output_db:
            output_db.write(json.dumps(ids, indent=len(ids)))
            output_db.close()
        return 0

    def delete_category(self, value: str):
        if value in ['buy_nitro', 'support', 'i_won_giveaway']:
            return 2  # can't delete default category
        config = self.categories()
        emojis = self.categories_emojis()
        ids = self.categories_ids()
        if value not in config.keys():
            return 1  # category doesn't exist
        del config[value]
        del emojis[value]
        del ids[value]
        with open('../config/tickets_categories.json', "w") as output_db:
            output_db.write(json.dumps(config, indent=len(config)))
            output_db.close()
        with open('../config/tickets_emoji.json', "w") as output_db:
            output_db.write(json.dumps(emojis, indent=len(emojis)))
            output_db.close()
        with open('../config/tickets_categories_id.json', "w") as output_db:
            output_db.write(json.dumps(ids, indent=len(ids)))
            output_db.close()
        return 0

    def add_new_transcription_index(self, transcript_path: str):
        indexes = self.transcriptions_indexes()
        current_index = self.last_transcript_index() + 1

        indexes.update({f'{current_index}': f'{transcript_path}'})
        self.change_transcript_index(current_index)

        with open('../config/transcripts_indexes.json', "w") as output_db:
            output_db.write(json.dumps(indexes, indent=len(indexes)))
            output_db.close()
        return 0

    async def save_transcript(self, channel):
        path = json.load(open('../../config.json'))['general']['PATH']

        print(channel)
        transcript = await chat_exporter.export(channel=channel)
        if transcript is None:
            return

        counter = self.last_transcript_index() + 1

        content = transcript.replace(
            '<!--\nThis transcript was generated using: https://github.com/mahtoid/DiscordChatExporterPy\nIf you have any issues or suggestions - open an issue on the Github Repository or alternatively join discord.gg/mq3hYaJSfa\n\n\n\n-->\n\n',
            '')
        transcript = content

        file_path = None

        discord_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"[{counter}]{str(channel.name.replace('ticket-', ''))}.html",
        )

        return counter, file_path, discord_file

    def open_transcript(self, index):
        path = self.transcriptions_indexes()[f'{index}']
        webbrowser.open('file://' + path)
        return 0

    def embed(self):
        embed = discord.Embed(title="Open a ticket using this dropdown!",
                              description="Choose the category you need!\n"
                                          "(If you will try do some action which doesn't fit to chosen category you will not get any answer and ticket will be shortly closed by staff.)",
                              colour=discord.Colour.orange())
        return embed

    def embed_transcription(self, interaction):
        embed = discord.Embed(
            title=f'Transcription from `{str(interaction.channel)}`',
            colour=discord.Colour.orange())

        embed.add_field(name='Ticket closed by:', value='<@' + str(interaction.author.id) + '>')
        embed.add_field(name='Ticket closed on:', value='``' + str(time.strftime('%Y-%m-%d %H:%M:%S')) + '``')
        embed.add_field(name='Ticket category:\n', value='``' + str(interaction.channel.category) + '``')

        members_con = str()

        for member in interaction.channel.members:
            if not client.get_user(member.id).bot:
                members_con += '<@' + str(member.id) + '>\n'

        embed.add_field(name='Ticket members:', value=members_con)
        return embed

    def dropdown(self):
        categories = self.categories()

        options = list()

        for value, des in categories.items():
            name = value.replace('_', ' ')
            name = name[0].upper() + name[1:]
            if value in ['buy_nitro', 'support', 'i_won_giveaway']:
                emoji = self.config()['tickets_category_emoji'][value]
            else:
                emoji = self.categories_emojis()[value]
            options.append(SelectOption(value=value, label=name, description=categories[value], emoji=emoji))

        dropdown = Select(placeholder='Select ticket category:', options=options, custom_id='open_ticket')

        return dropdown

    def close_ticket_button(self):
        button = Button(label="Close ticket!", custom_id=f'close_ticket', style=ButtonStyle.red)
        return button

    def approve_closing_ticket_button(self):
        button = Button(label="Close ticket?", custom_id=f'approve_closing_ticket', style=ButtonStyle.red, emoji="✔️")
        return button

    def open_transcription_button(self, index: int):
        button = Button(label="Open transcription!", custom_id=f'open_transcription|{index}', style=ButtonStyle.green)
        return button
