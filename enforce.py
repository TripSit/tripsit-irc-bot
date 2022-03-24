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
    def cmdv(reason):
        ret = ''

        time = [resolve_time(t) for t in reason if resolve_time(t)]
        reason = [r for r in reason if not resolve_time(r)]
        ret += f'a duration of {time[0]}' if len(time) > 0 else 'indefinitely'
        if len(reason) == 0:
            return ret

        variant = [resolve_variant(v) for v in reason if resolve_variant(v)]
        reason = [r for r in reason if not resolve_variant(r)]
        ret += f' for {" ".join(reason)}' if len(reason) > 0 else ''

        ret += f' :: {variant[0]}' if len(variant) > 0 else ''
        return ret

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


def resolve_variant(var):
    match list(var):
        case ['#', *rem] if (''.join(rem)).lower() in ['kline', 'glo', 'underban', 'shadow']:
            return dict({'kline': '$KLINE',
                         'glo': '$GLOBAL',
                         'underban': '$UNDER',
                         'shadow': '$SHADOW'})[(''.join(rem)).lower()]
        case _:
            return None


def resolve_time(cand):
    print(cand)
    match list(cand):
        case (*nums, ('m' | 'h' | 'd') | ('minutes' | 'hours' | 'days') as timev) if ''.join(nums).isdigit():
            return f'{"".join(nums)} {dict({"m":"minutes", "h":"hours","d":"days"})[timev]}'
        case _:
            return None


def subvariant(f):
    match f:
        case '.mute':
            return 'Quieting'
        case '.cban':
            return 'Channel banning'
        case '.nban':
            return 'Applying network ban'
