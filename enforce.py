from sopel import plugin
from sopel.tools import events


@plugin.event(events.RPL_YOUREOPER)
def hello(bot, trigger):
    bot.say("Hello, " + trigger.nick +
            "! I'm a bot, and I'm here to enforce the rules of this channel. If you have any questions, please ask an operator.", 'winter')
    bot.say(f'Hi therre! {trigger.account}', 'winter')
    bot.say(f'we are in {trigger.sender}', 'winter')
    bot.say(f'your hostmask is {trigger.hostmask}', 'winter')
    bot.say(f'the args were {trigger.args}', 'winter')


@plugin.command('mute', 'cban', 'nban', 'teleport')
def say_hi(bot, trigger):
    # bot.say(f'Hi therre! {trigger.account}')
    # bot.say(f'we are in {trigger.sender}')
    # bot.say(f'your hostmask is {trigger.hostmask}')
    # bot.say(f'the args were {trigger.args}')
    resolve_command(bot, trigger.args[1])


def resolve_command(bot, arg):

    def resolve_variant(var):
        match list(var):
            case ['#', *rem] if (''.join(rem)).lower() in ['kline', 'glo', 'underban', 'shadow']:
                return 'penalty_variant', \
                    dict({'kline': '$KLINE',
                          'glo': '$GLOBAL',
                          'underban': '$UNDER',
                          'shadow': '$SHADOW'})[(''.join(rem)).lower()]
            case ['#', *rem]:
                name = f"#{''.join(rem)}"
                return ('channel', name) if bot.channels[name] is not None else ('error', 'unknown channel')
            case (*nums, ('m' | 'h' | 'd') | ('minutes' | 'hours' | 'days') as timev) if ''.join(nums).isdigit():
                return 'time', {
                    'amount': int(''.join(nums)),
                    'unit': dict({"m": "minutes", "h": "hours", "d": "days"})[timev]
                }
            case anything:
                return 'description', ''.join(anything)

    def cmdv(args):
        directives = list(map(resolve_variant, args))

        for k, v in directives:
            bot.say(f'{k}: {v}')

        return directives

    match arg.split():
        case [('.mute' | '.cban' | '.nban') as fate, *values]:
            fate = subvariant(fate)
            match values:
                case [user, *reason]:
                    bot.say(
                        f"{fate} {user} {cmdv(reason)}")
                case [user]:
                    bot.say(f"{fate} {user} indefinitely")
                case _:
                    bot.say(
                        f'Syntax: {fate} [user] [<reason*>|<time*>|<variant*> in any order]')
        case ['.teleport', user, *channels]:
            bot.say("Hello")
            if len(channels) == 1:
                bot.write(('SAJOIN', f'{user} {channels[0]}'))
            elif len(channels) == 2:
                bot.write(('KICK', f'{channels[0]} {user}'))
                bot.write(('SAJOIN', f'{user} {channels[1]}'))


def subvariant(f):
    match f:
        case '.mute':
            return 'Quieting'
        case '.cban':
            return 'Channel banning'
        case '.nban':
            return 'Applying network ban'
