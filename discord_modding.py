# System stuff
# import sys
# The star of the show!
import discord
# This allows us to define the bot's commands
from discord.ext import commands
# For slash commands
# from discord_slash import SlashCommand, SlashContext

# These are used to pull in the discord settings from the default.cfg file
from sopel.config.types import (
    StaticSection, ValidatedAttribute
)
# Load in the plugin features, since this is a plugin ( ͡° ͜ʖ ͡°)
from sopel import plugin as sopel_plugin
# Asyncio is used for discord's async functions
import asyncio
# Threading is used to start up a discord bot thread inside of this sopel module
import threading
# This is used for logging functions
import logging
# For random questions
import random
# For the database
import tempfile
import json
import os
from sopel.tools import Identifier
from sopel.db import (
    ChannelValues,
    NickIDs,
    Nicknames,
    NickValues,
    PluginValues,
    SopelDB,
)
# This is a fix for an asyncio issue on windows
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Discord Setup Information
DISCORD_API_VERSION = 6
DISCORD_API_URL = f'https://discord.com/api/v{DISCORD_API_VERSION}'
description = '''Moonbear's first discord module =3'''
# Define discord permissions
intents = discord.Intents(
    messages=True,
    members=True,
    presences=True,
    reactions=True,
    emojis=True,
    bans=True,
    voice_states=True
)

# To cache members and messages
member_cache = discord.MemberCacheFlags(
    online=True,  # Whether to cache members with a status. Members that go offline are no longer cached.
    voice=True,   # Whether to cache members that are in voice. Members that leave voice are no longer cached.
    joined=True   # Whether to cache members that joined the guild or are chunked as part of the initial log in flow. Members that leave the guild are no longer cached.
)
prefix = "."

# Set up the bot
discord_bot = commands.Bot(
    command_prefix=prefix,
    description=description,
    intents=intents,
    member_cache_flags=member_cache
)

# I cant get slash commands to work yet
# slash = SlashCommand(discord_bot)

# Handles log statements
logger = logging.getLogger(__name__)
# Comment this out to turn off debug logs
logger.setLevel(logging.DEBUG)
# Initialize this so we can inject processes into the running loop
loop = asyncio.get_event_loop()

# Setup the database
db_filename = tempfile.mkstemp()[1]

TMP_CONFIG = """
[core]
owner = Embolalia
db_filename = {db_filename}
"""


def db(configfactory):
    content = TMP_CONFIG.format(db_filename=db_filename)
    settings = configfactory('default.cfg', content)
    db = SopelDB(settings)
    # TODO add tests to ensure db creation works properly, too.
    return db


@sopel_plugin.require_admin
@sopel_plugin.command('dbgetnickid', 'getnickid', 'nickid')
@sopel_plugin.example('.dbgetnickid nick')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_get_nick_id(sopel_bot, trigger):
    nick = trigger.group(3)
    try:
        # Attempt to get nick ID: it is not created by default
        nick_id = sopel_bot.db.get_nick_id(nick)
    except ValueError:
        # Create the nick ID
        nick_id = sopel_bot.db.get_nick_id(nick, create=True)
    finally:
        output = f"Got {nick}'s NickId attribute as {nick_id}"
        logger.debug(output)
        sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command('dbset')
@sopel_plugin.example('.dbset nick key value')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_set(sopel_bot, trigger):
    nick = trigger.group(3)
    key = trigger.group(4)
    value = trigger.group(5)
    sopel_bot.db.set_nick_value(nick, key, value)
    output = f"Set {nick}'s {key} attribute to {value}"
    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command('dbget')
@sopel_plugin.example('.dbget nick key')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_get(sopel_bot, trigger):
    nick = trigger.group(3)
    key = trigger.group(4)
    try:
        found_value = json.loads(sopel_bot.db.get_nick_value(nick, key))
        output = f"Got {nick}'s {key} attribute as {found_value}"
        # print(f'Found {key}: {found_value[key]}')
    except TypeError:
        output = f"Did not find {nick}'s {key}"

    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command('dbaliasnick', 'setalias')
@sopel_plugin.example('.dbaliasnick nick alias')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_alias_nick(sopel_bot, trigger):
    nick = trigger.group(3)
    alias = trigger.group(4)
    nick_id = sopel_bot.db.get_nick_id(nick, create=True)
    try:
        sopel_bot.db.alias_nick(nick, alias)
    except ValueError:
        output = f"Set {nick}'s already has an alias of {alias}!"
        logger.debug(output)
        sopel_bot.reply(output)
        return
    assert nick_id == sopel_bot.db.get_nick_id(alias)
    output = f"Set {nick}'s alias as as {alias}"
    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command(
    'dbunaliasnick',
    'removealias',
    'forgetalias',
    'deletealias',
    'remalias',
    'delalias',
    'rmalias')
@sopel_plugin.example('.dbunaliasnick alias')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_unalias_nick(sopel_bot, trigger):
    alias = trigger.group(3)
    try:
        sopel_bot.db.unalias_nick(alias)
    except ValueError:
        output = f"{alias} doesnt exist as an alias!"
        logger.debug(output)
        sopel_bot.reply(output)
        return
    output = f"Removed {alias} an alias!"
    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command(
    'dbforgetnickgroup',
    'forgetnickgroup',
    'removenickgroup',
    'deletenickgroup',
    'remnickgroup',
    'delnickgroup',
    'rmnickgroup')
@sopel_plugin.example('.dbforgetnickgroup nick')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_forget_nick_group(sopel_bot, trigger):
    nick = trigger.group(3)
    try:
        sopel_bot.db.forget_nick_group(nick)
    except ValueError:
        output = f"{nick} doesnt exist as a nick group!"
        logger.debug(output)
        sopel_bot.reply(output)
        return
    output = f"Removed {nick} from the db!"
    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command('dbmergenickgroup', 'mergenickgroup', 'mergenicks')
@sopel_plugin.example('.dbmergenickgroup nick alias')
@sopel_plugin.output_prefix('[DB] ')
def irc_db_merge_nick_group(sopel_bot, trigger):
    nick = trigger.group(3)
    alias = trigger.group(4)
    try:
        sopel_bot.db.merge_nick_groups(nick, alias)
    except ValueError:
        output = f"{nick} doesnt exist as a nick group, or something!"
        logger.debug(output)
        sopel_bot.reply(output)
        return
    output = f"Merged {nick} and {alias}!"
    logger.debug(output)
    sopel_bot.reply(output)


@sopel_plugin.require_admin
@sopel_plugin.command('dmute', 'discordmute')
@sopel_plugin.example('.dmute nick')
@sopel_plugin.output_prefix('[DB] ')
def irc_mute(sopel_bot, trigger):
    # This is the mute functionality on the IRC side
    user_name = trigger.group(3)
    reason = "I was lazy and didnt give a reason"
    if trigger.group(4):
        reason = trigger.group(4)
    asyncio.run_coroutine_threadsafe(discord_mute(sopel_bot, user_name, reason), loop)


async def discord_mute(sopel_bot, user_name, reason):
    # This is the mute functionality on the Discord side
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        await member_object.add_roles(muted_role, reason=f"Muted via IRC for: {reason}")
        logger.info(f"[discord] Muted {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")
        sopel_bot.reply(f"[discord]  Muted {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")


@sopel_plugin.require_admin
@sopel_plugin.command('dunmute', 'discordunmute')
def irc_unmute(sopel_bot, trigger):
    user_name = trigger.group(3)
    asyncio.run_coroutine_threadsafe(discord_unmute(sopel_bot, user_name), loop)


async def discord_unmute(sopel_bot, user_name):
    member_object = await MyDiscordClient.lookup_discord_member(user_name)
    if member_object:
        await member_object.remove_roles(muted_role, reason="Unmuted via IRC")
        logger.info(f"[discord] Unmuted {member_object.name}#{member_object.discriminator} ({member_object.nick})")
        sopel_bot.reply(f"[discord] Unmuted {member_object.name}#{member_object.discriminator} ({member_object.nick})")


@sopel_plugin.require_admin
@sopel_plugin.command('dkick', 'discordkick')
def irc_Kick(sopel_bot, trigger):
    user_name = trigger.group(3)
    reason = "I was lazy and didnt give a reason"
    if trigger.group(4):
        reason = trigger.group(4)
    asyncio.run_coroutine_threadsafe(discord_kick(sopel_bot, user_name, reason), loop)


async def discord_kick(sopel_bot, user_name, reason):
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        logger.debug(f"[discord] Attempting to kick {member_object}")
        try:
            await guild.kick(member_object, reason=f"Kicked via IRC for: {reason}")
        except Exception as e:
            logger.critical(e)
            sopel_bot.reply(e)
        logger.info(f"[discord] Kicked {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")
        sopel_bot.reply(f"[discord] Kicked {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")


@sopel_plugin.require_admin
@sopel_plugin.command('dban', 'discordban')
def irc_ban(sopel_bot, trigger):
    user_name = trigger.group(3)
    reason = "I was lazy and didnt give a reason"
    if trigger.group(4):
        reason = trigger.group(4)
    asyncio.run_coroutine_threadsafe(discord_ban(sopel_bot, user_name, reason), loop)


async def discord_ban(sopel_bot, user_name, reason):
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        logger.debug(f"[discord] Attempting to ban {member_object}")
        try:
            await guild.ban(member_object, reason=f"Kicked via IRC for: {reason}", delete_message_days=7)
        except Exception as e:
            logger.critical(e)
            sopel_bot.reply(e)
        logger.info(f"[discord] Banned {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")
        sopel_bot.reply(f"[discord] Banned {member_object.name}#{member_object.discriminator} ({member_object.nick}) for {reason}")


@sopel_plugin.require_admin
@sopel_plugin.command('drename', 'discordrename', 'dsvsnick', 'discordsvsnick')
def irc_rename(sopel_bot, trigger):
    user_name = trigger.group(3)
    new_name = trigger.group(4)
    asyncio.run_coroutine_threadsafe(discord_rename(sopel_bot, user_name, new_name), loop)


async def discord_rename(sopel_bot, user_name, new_name):
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        logger.debug(f"[discord] Attempting to change name on {member_object}")
        try:
            await member_object.edit(nick=new_name)
        except Exception as e:
            logger.critical(e)
            sopel_bot.reply(e)
        logger.info(f"[discord] Renamed {user_name} to {new_name}")
        sopel_bot.reply(f"[discord] Renamed {user_name} to {new_name}")


@sopel_plugin.require_admin
@sopel_plugin.command('dadd_role', 'dset_role', 'dsetrole', 'daddroll')
def irc_add_roles(sopel_bot, trigger):
    user_name = trigger.group(3)
    role_name = trigger.group(4)
    reason = trigger.group(5)
    roles = guild.roles
    role_id = 0
    for role in roles:
        if role_name == role.name:
            role_id = role.id
            break

    if role_id == 0:
        sopel_bot.reply(f"[discord] Role not found, try using {prefix}roles")

    asyncio.run_coroutine_threadsafe(discord_add_roles(sopel_bot, user_name, role_id, reason), loop)


async def discord_add_roles(sopel_bot, user_name, role_name, role_id, reason):
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        logger.debug(f"[discord] Attempting to add role on {member_object}")
        try:
            await member_object.add_roles([role_id], reason=reason)
        except Exception as e:
            logger.critical(e)
            sopel_bot.reply(e)
        logger.info(f"[discord] Set {role_name} on {user_name}")
        sopel_bot.reply(f"[discord] Set {role_name} on {user_name}")


@sopel_plugin.require_admin
@sopel_plugin.command('dremove_role', 'dremoverole', 'dremrole')
def irc_remove_roles(sopel_bot, trigger):
    user_name = trigger.group(3)
    role_name = trigger.group(4)
    reason = trigger.group(5)
    roles = guild.roles
    role_id = 0
    for role in roles:
        if role_name == role.name:
            role_id = role.id
            break

    if role_id == 0:
        sopel_bot.reply(f"[discord] Role not found, try using {prefix}roles")

    asyncio.run_coroutine_threadsafe(discord_remove_roles(sopel_bot, user_name, role_id, reason), loop)


async def discord_remove_roles(sopel_bot, user_name, role_name, role_id, reason):
    member_object = await MyDiscordClient.lookup_discord_member(sopel_bot, user_name)
    if member_object:
        logger.debug(f"[discord] Attempting to remove role on {member_object}")
        try:
            await member_object.add_roles([role_id], reason=reason)
        except Exception as e:
            logger.critical(e)
            sopel_bot.reply(e)
        logger.info(f"[discord] Removed {role_name} on {user_name}")
        sopel_bot.reply(f"[discord] Removed {role_name} on {user_name}")


@sopel_plugin.require_admin
@sopel_plugin.command('roles')
def irc_roles(sopel_bot, trigger):
    roles = guild.roles
    role_output = ""
    for role in roles:
        role_output += f"{role.name}: {role.id}"
    sopel_bot.reply(role_output)


# Start most of Discord specific stuff
class GuildSection(StaticSection):
    # This pulls information from the sopel config file
    # TODO: Set up the debug channel ID, guild ID, and muted rule ID
    discord_token = ValidatedAttribute('discord_token')
    botspam_channel_id = ValidatedAttribute('botspam_channel_id')
    sandbox_channel_id = ValidatedAttribute('sandbox_channel_id')
    welcome_channel_id = ValidatedAttribute('welcome_channel_id')
    guild_id = ValidatedAttribute('guild_id')
    muted_role_id = ValidatedAttribute('muted_role_id')


def setup(bot):
    # This defines the section of the sopel_plugin used for the sopel bot
    global sopel_bot
    sopel_bot = bot
    sopel_bot.config.define_section('discord', GuildSection)
    global sandbox_channel_id
    sandbox_channel_id = sopel_bot.config.discord.sandbox_channel_id
    global botspam_channel_id
    botspam_channel_id = sopel_bot.config.discord.botspam_channel_id
    global welcome_channel_id
    welcome_channel_id = sopel_bot.config.discord.welcome_channel_id
    global guild_id
    guild_id = sopel_bot.config.discord.guild_id
    global muted_role_id
    muted_role_id = sopel_bot.config.discord.muted_role_id
    logger.info(f"[discord] GuildID: {guild_id} | MutedID: {muted_role_id} | BotspamID: {botspam_channel_id} | SandboxID: {sandbox_channel_id}")
    discord_client.irc_bot = sopel_bot
    # If the bot isnt already running, connect to discord
    if not loop.is_running():
        loop.create_task(discord_client.start(sopel_bot.config.discord.discord_token))
        t = threading.Thread(target=run_discord, args=(loop,))
        t.start()


def configure(config):
    """
    | name               | example | purpose                        |
    | ----               | ------- | -------                        |
    | discord_token      | 12345   | Login to bot                   |
    | botspam_channel_id | 12345   | Channel to send messages       |
    | sandbox_channel_id | 12345   | Channel to send messages       |
    | guild_id           | 12345   | Identify which server to act on|
    | muted_role_id      | 12345   | To mute users                  |
    """
    config.define_section('discord', GuildSection)
    config.discord.configure_setting(
        'discord_token',
        'Enter the token of the bot that will connect to your server!'
        'Do not share this token with anyone, this is being saved do your local config file!'
    )
    config.discord.configure_setting(
        'botspam_channel_id',
        'This is the channel ID of the room that will output what the bot does'
    )
    config.discord.configure_setting(
        'sandbox_channel_id',
        'This is the channel ID of the room that will output what the bot does DURING DEVELOPMENT'
    )
    config.discord.configure_setting(
        'welcome_channel_id',
        'This is the channel ID of the room that will output random questions to users that join'
    )
    config.discord.configure_setting(
        'guild_id',
        'This is the ID of the guild that the bot is connecting to'
    )
    config.discord.configure_setting(
        'muted_role_id',
        'This is the ID of the role that is used for muting'
    )


def run_discord(loop):
    # This runs the connection to discord, forever >=)
    loop.run_forever()


class MyDiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        logger.info("[discord] Connected")

    async def on_disconnect(self):
        logger.info("[discord] Disconnected")

    async def on_resumed(self):
        logger.info("[discord] Resumed")

    async def on_ready(self):
        # This will be sent to the console when logged into discord
        logger.info(f"[discord] logged in as {discord_client.user.name}, id: {discord_client.user.id}")
        # We initialize stuff we're going to re-use here.
        # We can't initialize this at the main level because we're not connected yet
        global sandbox_channel
        sandbox_channel = discord_client.get_channel(int(sandbox_channel_id))
        global botspam_channel
        botspam_channel = discord_client.get_channel(int(botspam_channel_id))
        global welcome_channel
        welcome_channel = discord_client.get_channel(int(welcome_channel_id))
        global guild
        guild = discord_client.get_guild(int(guild_id))
        logger.info(f"[discord] Connected to {guild.name} discord and outputting to the {sandbox_channel.name} room")
        await sandbox_channel.send(f"[discord] Connected to {guild.name} discord and outputting to the {sandbox_channel.name} room")
        global muted_role
        muted_role = guild.get_role(int(muted_role_id))

    async def on_member_join(self, member):
        logger.info(f"{member.name} has joined!")
        # await welcome_channel.send(random.choice(question_list))
        await asyncio.sleep(0)

    async def on_raw_reaction_add(self, payload):
        '''
        <RawReactionActionEvent
            message_id=int
            user_id=int
            channel_id=int
            guild_id=int
            emoji=<PartialEmoji
                animated=bool
                name='emoji'
                id=None>
            event_type='REACTION_ADD'
            member=<Member
                id=int
                name='str'
                discriminator='int'
                bot=False
                nick='str'
                guild=<Guild
                    id=int
                    name='str'
                    shard_id=None
                    chunked=False
                    member_count=int
                >
            >
        >
        '''
        # logger.debug(payload)
        channel = discord_client.get_channel(int(payload.channel_id))
        message = await channel.fetch_message(payload.message_id)
        emoji_name = payload.emoji.name
        giver_nick = f"{payload.member.name}#{payload.member.discriminator}"
        taker_nick = f"{message.author.name}#{message.author.discriminator}"
        outputA = f"{giver_nick} added {emoji_name} to {taker_nick} in {channel.name}"
        logger.info(outputA)
        await sandbox_channel.send(outputA)
        if giver_nick == taker_nick:
            output = "Users cannot give themselves awards so ignoring this!"
            logger.info(output)
            await sandbox_channel.send(output)
            return

        taker_count = 1
        taker_emojis = sopel_bot.db.get_nick_value(taker_nick, "emoji-taken")
        if taker_emojis:
            logger.debug(f"{taker_nick}'s emojis: {taker_emojis}")
            for key in taker_emojis:
                # logger.debug(f"{key}: {taker_emojis[key]}")
                if key == emoji_name:
                    taker_count = taker_emojis[key] + 1
                    taker_emojis[emoji_name] = taker_count
            if taker_count == 1:
                taker_emojis[emoji_name] = taker_count
        else:
            logger.debug("Creating new emoji group!")
            taker_emojis = json.loads('{"' + emoji_name + '":' + str(taker_count) + '}')
        output = f"{taker_nick} has received {emoji_name} from {taker_count} people!"
        logger.info(output)
        await sandbox_channel.send(output)
        logger.debug(f"Setting {taker_nick}'s 'emoji-taken' to {taker_emojis}")
        sopel_bot.db.set_nick_value(taker_nick, "emoji-taken", taker_emojis)

        giver_count = 1
        giver_emojis = sopel_bot.db.get_nick_value(giver_nick, "emoji-given")
        if giver_emojis:
            logger.debug(giver_emojis)
            for key in giver_emojis:
                # logger.debug(f"{key}: {taker_emojis[key]}")
                if key == emoji_name:
                    giver_count = giver_emojis[key] + 1
                    giver_emojis[emoji_name] = giver_count
            if giver_count == 1:
                giver_emojis[emoji_name] = giver_count
        else:
            logger.debug("Creating new emoji group!")
            giver_emojis = json.loads('{"' + emoji_name + '":' + str(giver_count) + '}')
        output = f"{giver_nick} has given {emoji_name} to {giver_count} people!"
        logger.info(output)
        await sandbox_channel.send(output)
        logger.debug(f"Setting {giver_nick}'s 'emoji-given' to {giver_emojis}")
        sopel_bot.db.set_nick_value(giver_nick, "emoji-given", giver_emojis)

    async def on_raw_reaction_remove(self, payload):
        '''
        <RawReactionActionEvent
            message_id=int
            user_id=int
            channel_id=int
            guild_id=int
            emoji=<PartialEmoji
                animated=bool
                name='emoji'
                id=None>
            event_type='REACTION_REMOVE'
            member=None
        >
        '''
        # logger.debug(payload)
        channel = discord_client.get_channel(int(payload.channel_id))
        message = await channel.fetch_message(payload.message_id)
        emoji_name = payload.emoji.name
        giver_nick = f"{message.author}"
        member = await guild.fetch_member(payload.user_id)
        # logger.debug(member)
        taker_nick = f"{member.name}#{member.discriminator}"
        output = f"{taker_nick} removed {emoji_name} from {giver_nick} in {channel.name}"
        logger.info(output)
        await sandbox_channel.send(output)

        taker_emojis = sopel_bot.db.get_nick_value(taker_nick, "emoji-given")
        logger.debug(f"{taker_nick}'s emojis: {taker_emojis}")
        try:
            for key in taker_emojis:
                # logger.debug(f"{key}: {taker_emojis[key]}")
                if key == emoji_name:
                    taker_count = taker_emojis[key] - 1
                    taker_emojis[emoji_name] = taker_count
        except Exception:
            logger.debug("Idk what happened so i decided not to do anything about it!")
        output = f"{taker_nick} has received {emoji_name} from {taker_count} people!"
        logger.info(output)
        await sandbox_channel.send(output)
        logger.debug(f"Setting {taker_nick}'s 'emoji-given' to {taker_emojis}")
        sopel_bot.db.set_nick_value(taker_nick, "emoji-given", taker_emojis)

        giver_count = 1
        giver_emojis = sopel_bot.db.get_nick_value(giver_nick, "emoji-taken")
        logger.debug(giver_emojis)
        try:
            for key in giver_emojis:
                # logger.debug(f"{key}: {taker_emojis[key]}")
                if key == emoji_name:
                    giver_count = giver_emojis[key] - 1
                    giver_emojis[emoji_name] = giver_count
            if giver_count == 1:
                giver_emojis[emoji_name] = giver_count
        except Exception:
            logger.debug("Idk what happened so i decided not to do anything about it!")
        output = f"{giver_nick} has given {emoji_name} to {giver_count} people!"
        logger.info(output)
        await sandbox_channel.send(output)
        logger.debug(f"Setting {giver_nick}'s 'emoji-taken' to {giver_emojis}")
        sopel_bot.db.set_nick_value(giver_nick, "emoji-taken", giver_emojis)

    async def on_raw_message_delete(self, payload):
        '''
        <Message
            id=956637760603697202
            channel=<TextChannel
                id=943599582921756732
                name='sandbox'
                position=24
                nsfw=False
                news=False
                category_id=538811330774171655
            >
            type=<MessageType.default:
                0
            >
            author=<Member
                id=177537158419054592
                name='MoonBear'
                discriminator='4874'
                bot=False
                nick='Moonbear'
                guild=<Guild
                    id=179641883222474752
                    name='TripSit'
                    shard_id=None
                    chunked=False
                    member_count=995
                >
            >
            flags=<MessageFlags value=0>
        >
        '''
        output = f"{payload.cached_message.author.name}#{payload.cached_message.author.discriminator} deleted a message in {payload.cached_message.channel.name}"
        # await sandbox_channel.send(output)
        logger.info(output)

    async def on_raw_message_edit(self, payload):
        '''
        <RawMessageUpdateEvent
            message_id=int
            channel_id=int
            guild_id=int
            data={
                'type': 0,
                'tts': False,
                'timestamp': 'dateTime',
                'pinned': False,
                'mentions': [],
                'mention_roles': [],
                'mention_everyone': False,
                'member': {
                    'roles': [
                        'int', 'int'
                    ],
                    'premium_since': None,
                    'pending': False,
                    'nick': 'str',
                    'mute': False,
                    'joined_at': 'dateTime',
                    'hoisted_role': 'int',
                    'deaf': False,
                    'communication_disabled_until': None,
                    'avatar': None,
                    'user': {
                        'username': 'str',
                        'id': int,
                        'avatar': 'hash',
                        'discriminator': 'int',
                        'bot': bool
                    }
                },
                'id': 'int',
                'flags': 0,
                'embeds': [],
                'edited_timestamp': 'dateTime',
                'content': 'str',
                'components': [],
                'channel_id': 'int',
                'author': {
                    'username': 'str',
                    'public_flags': 0,
                    'id': 'int',
                    'discriminator': 'int',
                    'avatar': 'hash'
                },
                'attachments': [],
                'guild_id': 'int'
            }
            cached_message=<Message
                id=int
                channel=<TextChannel
                    id=int
                    name='sandbox'
                    position=26
                    nsfw=False
                    news=False
                    category_id=int
                >
                type=<MessageType.default:
                    0
                >
                author=<Member
                    id=int
                    name='str'
                    discriminator='int'
                    bot=False
                    nick='str'
                    guild=<Guild
                        id=int
                        name='str'
                        shard_id=None
                        chunked=False
                        member_count=int
                    >
                >
                flags=<MessageFlags
                    value=0
                >
            >
        >
        '''
        output = f"{payload.cached_message.author.name}#{payload.cached_message.author.discriminator} edited a message in {payload.cached_message.channel.name}"
        # await sandbox_channel.send(output)
        logger.info(output)

    async def on_message(self, message):
        '''
        <Message
            id=956988322230730802
            channel=<TextChannel
                id=943599582921756732
                name='sandbox'
                position=26
                nsfw=False
                news=False
                category_id=538811330774171655
            >
            type=<MessageType.default:
                0
            >
            author=<Member
                id=177537158419054592
                name='MoonBear'
                discriminator='4874'
                bot=False
                nick='Moonbear'
                guild=<Guild
                    id=179641883222474752
                    name='TripSit'
                    shard_id=None
                    chunked=False
                    member_count=994
                >
            >
            flags=<MessageFlags
                value=0
            >
        >
        '''
        # This section handles messages from Discord
        content = message.clean_content
        if message.author.bot:
            return

        logger.debug(f"[discord] Messsage from <{message.author.name}> in #{message.channel.name}: {content}")
        # logger.debug(message)

        can_mute = message.author.guild_permissions.manage_roles
        can_kick = message.author.guild_permissions.kick_members
        can_ban = message.author.guild_permissions.ban_members
        is_admin = message.author.guild_permissions.administrator
        author_roles = message.author.roles
        role_vip = False
        # role_helper = False
        # role_needshelp = False

        for role_obj in author_roles:
            if role_obj.name == "VIP":
                role_vip = True
            # if role_obj.name == "Helper":
            #     role_helper = True
            # if role_obj.name == "NeedsHelp":
            #     role_needshelp = True

        if message.content.startswith(f'{prefix}topic'):
            await message.channel.send(random.choice(question_list))

        if role_vip:
            if message.content.startswith(f'{prefix}awards'):
                try:
                    user_name = content.split(" ")[1]
                except Exception:
                    await message.channel.send(f'You need to supply username! EG: {prefix}awards username')

                member = await MyDiscordClient.lookup_discord_member(self, user_name)
                member_username = f"{member.name}#{member.discriminator}"
                logger.debug(f"Looking for awards {member_username} has {type}")
                taken_emojis = sopel_bot.db.get_nick_value(member_username, "emoji-taken")
                given_emojis = sopel_bot.db.get_nick_value(member_username, "emoji-given")
                output = f"{member_username} has recieved: {taken_emojis}\n{member_username} has given: {given_emojis}"
                logger.debug(output)
                await message.channel.send(output)

            if message.content.startswith(f'{prefix}letshelp'):
                needshelp_role = guild.get_role(955853983287754782)
                try:
                    user_name = content.split(" ")[1]
                except Exception:
                    await message.channel.send('You need to supply a user!')
                member_object = await MyDiscordClient.lookup_discord_member(self, user_name)
                await message.channel.send(f'I will start helping {user_name}!')
                await member_object.add_roles(needshelp_role)

            if message.content.startswith(f'{prefix}wehelped'):
                needshelp_role = guild.get_role(955853983287754782)
                try:
                    user_name = content.split(" ")[1]
                except Exception:
                    await message.channel.send('You need to supply a user!')
                member_object = await MyDiscordClient.lookup_discord_member(self, user_name)
                await message.channel.send(f'I will stop helping {user_name}!')
                await member_object.remove_roles(needshelp_role)

            if message.content.startswith(f'{prefix}hello'):
                await message.channel.send('Hello!')

            if message.content.startswith(f'{prefix}js'):
                await message.channel.send('>=(')

            if message.content.startswith(f'{prefix}welcome'):
                await welcome_channel.send("Wecome to the TripSit discord! You'll need to talk in this channel a bit to access the rest of the network, here's a question to get you started!")
                await welcome_channel.send(random.choice(question_list))

        if can_mute:
            if message.content.startswith(f'{prefix}quiet'):
                await sandbox_channel.send("I would quiet someone on IRC now, but i dont know how!")
        if can_kick:
            if message.content.startswith(f'{prefix}kick'):
                await sandbox_channel.send("I would kick someone on IRC now, but i dont know how!")
        if can_ban:
            if message.content.startswith(f'{prefix}nban'):
                await sandbox_channel.send("I would ban someone on IRC now, but i dont know how!")
            if message.content.startswith(f'{prefix}svsnick'):
                await sandbox_channel.send("I would change someone's nickname on IRC now, but i dont know how!")

        if is_admin:
            if message.content.startswith(f'{prefix}roles'):
                roles = guild.roles
                role_output = ""
                for role in roles:
                    role_output += f"{role.name}: {role.id}\r\n"
                logger.debug(role_output)
                await message.channel.send(role_output)

            if message.content.startswith(f'{prefix}cache'):
                log = ""
                for each in discord_client.cached_messages:
                    log = log + f"{each.author.name}: {each.clean_content}" + "\r\n"
                    logger.info(each)
                await message.channel.send(log)

            if message.content.startswith(f'{prefix}invite'):
                my_invite = await guild.text_channels[0].create_invite()
                print(my_invite)
                return

            if message.content.startswith(f'{prefix}reload'):
                await sandbox_channel.send("Reloading sopel plugins!")
                logger.info("Reloading sopel plugins!")
                discord_client.irc_bot.reload_plugins()
                await sandbox_channel.send("Done!")
                logger.info("Done!")

            if message.content.startswith(f'{prefix}restart'):
                restart_message = f"Received Restart command from {message.author.name} in #{message.channel.name}"
                await sandbox_channel.send(restart_message)
                logger.info(restart_message)
                discord_client.irc_bot.restart(restart_message)

            if message.content.startswith(f'{prefix}quit'):
                quit_message = f"Received Quit command from {message.author.name} in #{message.channel.name}"
                await sandbox_channel.send(quit_message)
                logger.info(quit_message)
                discord_client.irc_bot.quit(quit_message)

        await asyncio.sleep(0)

    async def lookup_discord_member(sopel_bot, user_name):
        # This function handles looking up the user in discord from IRC
        logger.debug(f"[discord] Processing {user_name}")
        try:
            # Try to turn the username into an integeger, in case the UserID was used
            user_name = int(user_name)
            logger.debug(f"[discord] Looking for the user ID {user_name}")
            matching_members = await guild.query_members(user_ids=[user_name])
        except ValueError:
            logger.debug(f"[discord] Looking for the user name {user_name}")
            matching_members = await guild.query_members(query=user_name)
        logger.debug(matching_members)

        if not matching_members:
            logger.debug(f"[discord] Could not find {user_name} on this server!")
            try:
                sopel_bot.reply(f"[discord] Could not find {user_name} on this server!")
            except Exception:
                pass

        if len(matching_members) > 1:
            logger.debug(f"[discord] Multiple results for {user_name}, pick one:")
            sopel_bot.reply(f"[discord] Multiple results for {user_name}, pick one:")
            for member in matching_members:
                logger.debug(f"[discord] Nickname: {member.nick} | DiscordID: {member.name}#{member.discriminator} | UserID: {member.id}")
                try:
                    sopel_bot.reply(f"[discord] Nickname: {member.nick} | DiscordID: {member.name}#{member.discriminator} | UserID: {member.id}")
                except Exception:
                    pass

        if len(matching_members) == 1:
            logger.debug(f"[discord] Found a single match for {user_name}")
            member_object = matching_members[0]
            return member_object


'''
    # TODO better error logging
    # async def on_error(self, event, *args, **kwargs):
    #     logger.critical(event)
    #     logger.critical(sys.exc_info())

    # @slash.slash(name="test")
    # async def test(ctx: SlashContext):
    #     embed = discord.Embed(title="Embed Test")
    #     await ctx.send(embed=embed)

    # async def on_raw_bulk_message_delete(self, payload):
    #     # Never seen this
    #     logger.info(f"Messages deleted: {payload}")

    # async def on_raw_reaction_clear(self, payload):
    #     # Not sure ive ever seen this?
    #     logger.info(f"{payload}")

    # async def on_raw_reaction_clear_emoji(self, payload):
    #     # Not sure ive ever seen this?
    #     logger.info(f"{payload}")

    # This doesnt work, perhaps for the same reason the below functiosn dont work?
    # @discord_bot.command()
    # async def ping(ctx):
    #     channel = discord_client.get_channel(943599582921756732)
    #     await channel.send('hello discord world!')
    #     await ctx.send("Pong!")

    # These don't work, use the RAW methods until Eric can figure out why
    # It's something to do with the asyncio loop i think
    # There is a message cache, but for some reason it's not accessible?
    # check the "cache" function above
    # async def on_message_delete(self, message):
    #     logger.info(f"Message deleted: {message}")

    # async def on_reaction_add(self, reaction, user):
    #     logger.info(f"{user} added {reaction}")

    # async def on_reaction_remove(self, reaction, user):
    #     logger.info(f"{user} removed {reaction}")

    # async def on_reaction_clear(self, message, reactions):
    #     logger.info(f"{message} removed {reactions}")

    # async def on_reaction_clear_emoji(self, reaction):
    #     logger.info(f"Cleared {reaction}")

    # async def on_bulk_message_delete(self, messages):
    #     logger.info(f"Messages deleted: {messages}")

    # async def on_message_edit(self, before, after):
    #     logger.info(f"Messages edited: {before} to {after}")
'''

question_list = ["What did you eat for breakfast?",
                 "How many cups of coffee, tea, or beverage-of-choice do you have each morning?",
                 "Are you an early bird or night owl?",
                 "Do you prefer showing at morning or night?",
                 "What's your favorite flower or plant?",
                 "What's your caffeinated beverage of choice? Coffee? Cola? Tea?",
                 "What's your favorite scent?",
                 "What's the last great TV show or movie you watched?",
                 "Best book you've ever read?",
                 "If you could learn one new professional skill, what would it be?",
                 "If you could learn one new personal skill, what would it be?",
                 "What's your favorite way to get in some exercise?",
                 "If you could write a book, what genre would you write it in? Mystery? Thriller? Romance? Historical fiction? Non-fiction?",
                 "What is one article of clothing that someone could wear that would make you walk out on a date with them?",
                 "The zombie apocalypse is coming, who are 3 people you want on your team?",
                 "What is your most used emoji?",
                 "Who was your childhood actor/actress crush?",
                 "If you were a wrestler what would be your entrance theme song?",
                 "If you could bring back any fashion trend what would it be?",
                 "You have your own late night talk show, who do you invite as your first guest?",
                 "You have to sing karaoke, what song do you pick?",
                 "What was your least favorite food as a child? Do you still hate it or do you love it now?",
                 "If you had to eat one meal everyday for the rest of your life what would it be?",
                 "If aliens landed on earth tomorrow and offered to take you home with them, would you go?",
                 "60s, 70s, 80s, 90s: Which decade do you love the most and why?",
                 "What's your favorite sandwich and why?",
                 "What is your favorite item you've bought this year?",
                 "What would be the most surprising scientific discovery imaginable?",
                 "What is your absolute dream job?",
                 "What would your talent be if you were Miss or Mister World?",
                 "What would the title of your autobiography be?",
                 "Say you're independently wealthy and don't have to work, what would you do with your time?",
                 "If you had to delete all but 3 apps from your smartphone, which ones would you keep?",
                 "What is your favorite magical or mythological animal?",
                 "What does your favorite shirt look like?",
                 "Who is your favorite Disney hero or heroine? Would you trade places with them?",
                 "What would your dream house be like?",
                 "If you could add anyone to Mount Rushmore who would it be; why?",
                 "You're going sail around the world, what's the name of your boat?",
                 "What fictional family would you be a member of?",
                 "What sport would you compete in if you were in the Olympics (even if it's not in the olympics)?",
                 "What would your superpower be and why?",
                 "What's your favorite tradition or holiday?",
                 "What fictional world or place would you like to visit?",
                 "What is your favorite breakfast food?",
                 "What is your favorite time of the day and why?",
                 "Coffee or tea?",
                 "Teleportation or flying?",
                 "What is your favorite TV show?",
                 "What book, movie read/seen recently you would recommend and why?",
                 "What breed of dog would you be?",
                 "If you had a time machine, would go back in time or into the future?",
                 "Do you think you could live without your smartphone (or other technology item) for 24 hours?",
                 "What is your favorite dessert?",
                 "What was your favorite game to play as a child?",
                 "Are you a traveler or a homebody?",
                 "What's one career you wish you could have?",
                 "What fictional world or place would you like to visit?",
                 "Have you ever completed anything on your “bucket list”?",
                 "Do you have a favorite plant?",
                 "What did you have for breakfast this morning?",
                 "What is your favorite meal to cook and why?",
                 "What is your favorite musical instrument and why?",
                 "Are you a cat person or a dog person?",
                 "What languages do you know how to speak?",
                 "Popcorn or M&Ms?",
                 "What's the weirdest food you've ever eaten?",
                 "What is your cellphone wallpaper?",
                 "You can have an unlimited supply of one thing for the rest of your life, what is it? Sushi? Scotch Tape?",
                 "Would you go with aliens if they beamed down to Earth?",
                 "Are you sunrise, daylight, twilight, or nighttime? Why?",
                 "What season would you be?",
                 "Are you a good dancer?",
                 "What fruit or vegetable would you most want to be?",
                 "If you could hang out with any cartoon character, who would you choose and why?",
                 "If you could live anywhere in the world for a year, where would it be?",
                 "If you could choose any person from history to be your imaginary friend, who would it be and why?",
                 "If you could see one movie again for the first time, what would it be and why?",
                 "If you could bring back any fashion trend what would it be?",
                 "If you could live in any country, where would you live?",
                 "If you could choose any two famous people to have dinner with who would they be?",
                 "If you could be any animal in the world, what animal would you choose to be?",
                 "If you could do anything in the world as your career, what would you do?",
                 "If you could be any supernatural creature, what would you be and why?",
                 "If you could change places with anyone in the world, who would it be and why?",
                 "If you could rename yourself, what name would you pick?",
                 "If you could have someone follow you around all the time, like a personal assistant, what would you have them do?",
                 "If you could instantly become an expert in something, what would it be?",
                 "If you could be guaranteed one thing in life (besides money), what would it be?",
                 "If you had to teach a class on one thing, what would you teach?",
                 "If you could magically become fluent in any language, what would it be?",
                 "If you could be immortal, what age would you choose to stop aging at and why?",
                 "If you could be on a reality TV show, which one would you choose and why?",
                 "If you could choose any person from history to be your imaginary friend, who would it be and why?",
                 "If you could eliminate one thing from your daily routine, what would it be and why?",
                 "If you could go to Mars, would you? Why or why not?",
                 "If you could have the power of teleportation right now, where would you go and why?",
                 "If you could write a book that was guaranteed to be a best seller, what would you write?",
                 "Would you rather live in the ocean or on the moon?",
                 "Would you rather meet your travel back in time to meet your ancestors or to the future to meet your descendants?",
                 "Would you rather lose all of your money or all of your pictures?",
                 "Would you rather have invisibility or flight?",
                 "Would you rather live where it only snows or the temperature never falls below 100 degrees?",
                 "Would you rather always be slightly late or super early?",
                 "Would you rather give up your smartphone or your computer?",
                 "Would you rather live without heat and AC or live without social media?",
                 "Would you rather be the funniest or smartest person in the room?",
                 "Would you rather be able to run at 100 miles per hour or fly at 10 miles per hour?",
                 "Would you rather be a superhero or the world's best chef?",
                 "Would you rather be an Olympic gold medallist or an astronaut?"]

# Initialize the "client" object
discord_client = MyDiscordClient()
