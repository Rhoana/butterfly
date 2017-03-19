# Allow Common Command Line / Module Interface

class Argv(object):

    @staticmethod
    # Python args to argv list
    def to_argv(*args, **flags):
        # Get positional and keyword arguments
        ordered = ['main'] + map(str, args)
        keyed = sorted(flags.items())
        # Flatten all keys and values
        return reduce(Argv.flat, keyed, ordered)

    @staticmethod
    # Add key-value pair to argv
    def flat(argv, key_value):
        # Get shorthand key, value
        k, v = map(str, key_value)
        # Make flag with one or two dashes
        flag = '--' if len(k) > 1 else '-'
        # Add the pair to the argv list
        return argv + [flag + k, v]
