"""
Eric's first sopel module =3
"""
# System stuff
import sys
# The star of the show!
import discord
# This allows us to define the bot's commands
from discord.ext import commands
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
# This is a fix for an asyncio issue on windows
import platform
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# For random questions
import random

# # This is an example command of how to run something
# @plugin.command('dev')
# def irc_dev(sopel_bot, trigger):
#     asyncio.run_coroutine_threadsafe(discord_dev(), loop)
# async def discord_dev():
#     await sandbox_channel.send("test!")

# Discord Setup Information
DISCORD_API_VERSION = 6
DISCORD_API_URL = f'https://discord.com/api/v{DISCORD_API_VERSION}'
description = '''Moonbear's first discord module =3'''
# intents = discord.Intents(
#     messages=True,
#     members=True,
#     presences=True,
#     reactions=True,
#     emojis=True,
#     bans=True,
#     voice_states=True
# )

# To cache members and messages
# member_cache = discord.MemberCacheFlags(
#     online=True,  # Whether to cache members with a status. Members that go offline are no longer cached.
#     voice=True,   # Whether to cache members that are in voice. Members that leave voice are no longer cached.
#     joined=True   # Whether to cache members that joined the guild or are chunked as part of the initial log in flow. Members that leave the guild are no longer cached.
# )
prefix = "."

# This is where we define the bot on discord
# intents = discord.Intents.all()
# member_cache = discord.MemberCacheFlags.all()
discord_bot = commands.Bot(
    command_prefix=prefix,
    description=description,
    intents=discord.Intents.all(),
    member_cache_flags=discord.MemberCacheFlags.all()
)

# Handles log statements
logger = logging.getLogger(__name__)
# Comment this out to turn off debug logs
logger.setLevel(logging.DEBUG)
# Initialize this so we can inject processes into the running loop
loop = asyncio.get_event_loop()


@sopel_plugin.require_admin
@sopel_plugin.command('mute')
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
@sopel_plugin.command('unmute')
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
@sopel_plugin.command('kick')
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
@sopel_plugin.command('ban')
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
@sopel_plugin.command('rename')
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

    async def on_error(self, event, *args, **kwargs):
        logger.critical(event)
        logger.critical(sys.exc_info())

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
                    member_count=int>>>
        '''
        logger.info(f"{payload.name}")

    async def on_raw_reaction_remove(self, payload):
        logger.info(f"{payload}")

    async def on_raw_reaction_clear(self, payload):
        logger.info(f"{payload}")

    async def on_raw_reaction_clear_emoji(self, payload):
        logger.info(f"{payload}")

    async def on_raw_message_delete(self, payload):
        logger.info(f"Message deleted: {payload}")

    async def on_raw_bulk_message_delete(self, payload):
        logger.info(f"Messages deleted: {payload}")

    async def on_raw_message_edit(self, payload):
        logger.info(f"Messages edited: {payload}")

    async def on_message(self, message):
        # This section handles messages from Discord
        content = message.clean_content
        if message.author.bot:
            return
        try:
            logger.debug(f"[discord] Messsage from <{message.author.name}> in #{message.channel.name}: {content}")
        except UnicodeEncodeError:
            logger.debug(f"[discord] Messsage from <{message.author.name}> in #{message.channel.name}")
        except Exception as e:
            logger.warning(e)

        can_mute = message.author.guild_permissions.manage_roles
        can_kick = message.author.guild_permissions.kick_members
        can_ban = message.author.guild_permissions.ban_members
        is_admin = message.author.guild_permissions.administrator

        if message.content.startswith(f'{prefix}hello'):
            await message.channel.send('Hello!')
        # if message.content.startswith(f'{prefix}cache'):
        #     log = ""
        #     for each in discord_client.cached_messages:
        #         log = log + f"{each.author.name}: {each.clean_content}" + "\r\n"
        #         logger.info(each)
        #     await message.channel.send(log)
        if message.content.startswith(f'{prefix}js'):
            await message.channel.send('>=(')
        if message.content.startswith(f'{prefix}welcome'):
            await welcome_channel.send("Wecome to the TripSit discord! You'll need to talk in this channel a bit to access the rest of the network, here's a question to get you started!")
            await welcome_channel.send(random.choice(question_list))
        if message.content.startswith(f'{prefix}topic'):
            await message.channel.send(random.choice(question_list))
        if message.content.startswith(f'{prefix}quiet') and can_mute:
            await sandbox_channel.send("I would quiet someone on IRC now, but i dont know how!")
        if message.content.startswith(f'{prefix}kick') and can_kick:
            await sandbox_channel.send("I would kick someone on IRC now, but i dont know how!")
        if message.content.startswith(f'{prefix}nban') and can_ban:
            await sandbox_channel.send("I would ban someone on IRC now, but i dont know how!")
        if message.content.startswith(f'{prefix}svsnick') and can_ban:
            await sandbox_channel.send("I would change someone's nickname on IRC now, but i dont know how!")

        if is_admin:
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
            sopel_bot.reply(f"[discord] Could not find {user_name} on this server!")

        if len(matching_members) > 1:
            logger.debug(f"[discord] Multiple results for {user_name}, pick one:")
            sopel_bot.reply(f"[discord] Multiple results for {user_name}, pick one:")
            for member in matching_members:
                logger.debug(f"[discord] Nickname: {member.nick} | DiscordID: {member.name}#{member.discriminator} | UserID: {member.id}")
                sopel_bot.reply(f"[discord] Nickname: {member.nick} | DiscordID: {member.name}#{member.discriminator} | UserID: {member.id}")
        if len(matching_members) == 1:
            logger.debug(f"[discord] Found a single match for {user_name}")
            member_object = matching_members[0]
            return member_object

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
