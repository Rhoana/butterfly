# Allow Common Command Line / Module Interface

class Argv(object):
    """ Uses to_argv to flatten arguments into a list
    """
    @staticmethod
    # Python args to argv list
    def to_argv(*args, **flags):
        """ Turns arguments and keywords into a list

        Arguments
        ----------
        args: list
            All in list must be able to become ``str``
        flags: dict
            All keys,values in dict must be able to \ 
                become ``str``

        Returns
        ---------
        list
            Allows :class:`argparse.ArgumentParser` to \ 
            handle a list and dictionary in the same way \ 
            that it would handle ``sys.argv``.
        """

        # Get positional and keyword arguments
        ordered = ['main'] + map(str, args)
        keyed = sorted(flags.items())
        # Flatten all keys and values
        return reduce(Argv.flat, keyed, ordered)

    @staticmethod
    def flat(argv, key_value):
        """Joins a key_value pair with an argv list

        Arguments
        ----------
        argv : list
            List of previously flattened arguments
        key_value : 2-list or 2-tuple
            Pair from dictionary to add to next list \ 
            of flattened arguments

        Returns
        --------
        list
            next list of flattened arguments
        """
        # Get shorthand key, value
        k, v = map(str, key_value)
        # Make flag with one or two dashes
        flag = '--' if len(k) > 1 else '-'
        # Add the pair to the argv list
        return argv + [flag + k, v]
