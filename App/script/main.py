from imports import *
from objects import *
from commends import AdminCommends, MemberCommends
from interactions import AdminInteractions, MemberInteractions

decoded_data = open('../../config.json', 'r').read().encode().decode('utf-8-sig')
open('../../config.json', 'w').write(decoded_data)

DiscordComponents(client)

commends = dict()

@tasks.loop(count=1)
async def wait_until_ready():
    if client.is_ready(): return
    await client.wait_until_ready()

    print(f'I am {client.user}')

    Queue()
    Prices()
    Tickets()

@client.event
async def on_message(message):
    # SLICED MESSAGE BY SPACES
    mess = message.content.split(' ')

    config = json.load(open('../../config.json'))
    config_gn = config['general']
    config_vs = config['velocitysniper']

    if len(mess[0]) > 1 and mess[0][0] == '$' and '__' not in mess[0]:
        mess[0] = mess[0].replace('$', '')
        if mess[0] in AdminCommends.__dict__.keys() and (message.author.id == config_gn['admin_id'] or message.author.id in config_gn['helpers_ids']):
            await AdminCommends.__dict__[mess[0]](AdminCommends(client, message))
        elif mess[0] in MemberCommends.__dict__.keys():
            await MemberCommends.__dict__[mess[0]](MemberCommends(client, message))

    elif message.channel.id == config_vs['velocity_stats_channel_id'] and message.author.id != config_gn['admin_id']:
        failed_claim_message_pattern = ":no: Attempted to claim code in `<DELAY>` | `<TYPE>`"
        success_claim_message_pattern = " <EMOJI> Successfully Claimed `<TYPE>` in `<DELAY>` <PING>!"
        time.sleep(0.5)
        embed = message.embeds[0]
        emb_dict = embed.to_dict()
        if emb_dict["title"] == "Failed Snipe!" or emb_dict["title"] == "Failed Snipe! (smart)":
            success = False
        elif emb_dict["title"] == "Sniped Nitro!" or emb_dict["title"] == "Sniped Nitro! (smart)":
            success = True
        else:
            return
        channel = client.get_channel(config_vs['claims_channel_id'])
        if success is False:
            delay = emb_dict["fields"][1]["value"]
            type = emb_dict["fields"][0]["value"]
            if 'Classic' in type or 'Basic' in type:
                emoji = '<a:Classic:1071536888357343252>'
            else:
                emoji = '<a:Boost:1071536882023944294>'
            await channel.send(
                failed_claim_message_pattern.replace("<DELAY>", delay).replace("<TYPE>", type).replace("<EMOJI>",
                                                                                                       emoji))
        if success is True:
            delay = emb_dict["fields"][1]["value"]
            type = emb_dict["fields"][0]["value"]

            if 'Classic' in type or 'Basic' in type:
                emoji = '<a:Classic:1071536888357343252>'
            else:
                emoji = '<a:Boost:1071536882023944294>'

            await channel.send(
                success_claim_message_pattern.replace("<DELAY>", delay).replace("<TYPE>", type).replace(
                    "<EMOJI>", emoji).replace("<PING>", f"<@&{config_vs['claims_ping_role_id']}>"))

            await Queue().safe_rerun_snipers(claimed=True)

    elif message.channel.id == config_gn['suggestions_channel_id'] and message.author.id != client.user.id:
        suggestion = message.content
        await message.delete()
        suggestion_embed = discord.Embed(title=f'Suggestion from {message.author}', description=suggestion, colour=discord.Colour.orange())
        suggestion_embed.set_footer(text=str(time.strftime('%Y-%m-%d %H:%M:%S')))
        suggestion_message = await message.channel.send(embed=suggestion_embed)
        await suggestion_message.add_reaction('✅')
        await suggestion_message.add_reaction('❌')


@client.event
async def on_button_click(interaction):
    config = json.load(open('../../config.json'))
    config_gn = config['general']

    cust_id = interaction.custom_id.split('|')[0]
    if len(interaction.custom_id.split('|')) == 1:
        special_arg = None
    else:
        special_arg = interaction.custom_id.split('|')[1]
    if cust_id in AdminInteractions.__dict__.keys() and (interaction.author.id == config_gn['admin_id'] or interaction.author.id in config_gn['helpers_ids']):
        await AdminInteractions.__dict__[cust_id](AdminInteractions(client, interaction, special_arg))
    elif cust_id in MemberInteractions.__dict__.keys():
        await MemberInteractions.__dict__[cust_id](MemberInteractions(client, interaction, special_arg))


@client.event
async def on_select_option(interaction):
    config = json.load(open('../../config.json'))
    config_gn = config['general']

    cust_id = interaction.custom_id.split('|')[0]
    if len(interaction.custom_id.split('|')) == 1:
        special_arg = None
    else:
        special_arg = interaction.custom_id.split('|')[1]
    if cust_id in AdminInteractions.__dict__.keys() and (interaction.author.id == config_gn['admin_id'] or interaction.author.id in config_gn['helpers_ids']):
        await AdminInteractions.__dict__[cust_id](AdminInteractions(client, interaction, special_arg))
    elif cust_id in MemberInteractions.__dict__.keys():
        await MemberInteractions.__dict__[cust_id](MemberInteractions(client, interaction, special_arg))


@tasks.loop(seconds=5)
async def _updating():
    if not client.is_ready(): return
    Prices()
    Queue()
    Tickets()


@tasks.loop(seconds=5)
async def stats_vs_channels():
    config = json.load(open('../../config.json'))
    config_gn = config['general']

    guild = client.get_guild(config_gn['guild_id'])

    all_claims = int(open('../config/all_claims.velocitysnipers').read())

    if config_gn['claims_stats_vc_id'] is not None:
        if client.get_channel(config_gn['claims_stats_vc_id']) is not None:
            await client.get_channel(config_gn['claims_stats_vc_id']).edit(name=f'👌〉Claims: {all_claims}')

    if config_gn['members_count_stats_vc_id'] is not None:
        if client.get_channel(config_gn['members_count_stats_vc_id']) is not None:
           members_counter = 0
           for member in guild.members:
               if str(config_gn['member_role_id']) in str(member.roles):
                   members_counter += 1
           await client.get_channel(config_gn['members_count_stats_vc_id']).edit(name=f'🙍‍〉Members: {members_counter}')

# CLIENT RUNNING
wait_until_ready.start()
_updating.start()
stats_vs_channels.start()

client.run(json.loads(open('../../config.json', 'r').read().encode().decode('utf-8-sig'))['general']['token'])
