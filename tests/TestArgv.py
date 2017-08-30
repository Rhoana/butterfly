import bfly
import unittest as ut
import logging as log
import sys

class TestArgv(ut.TestCase):
    """ set up tests for ``UtilityLayer.to_argv``
    """
    PORT = 2017
    # Log to the command line
    log_info = {
        'stream': sys.stdout,
        'level': log.INFO
    }
    # List some test cases and results
    TESTS = [
        {
        'IN':
            [
                [],
                {}
            ],
        'OUT': ['main']
        },
        {
        'IN':
            [
                [1337],
                {
                'exp': '~/data'
                }
            ],
        'OUT': ['main','1337','--exp','~/data']
        },
        {
        'IN':
            [
                [1,'3'],
                {
                'abc': 123,
                'a': '123'
                }
            ],
        'OUT': ['main','1','3','-a','123','--abc','123']
        }
    ]

    def test_argv(self):
        """ Test the ``UtilityLayer.to_argv``
        """
        # Log to command line
        log.basicConfig(**self.log_info)

        # Length Error
        def same_length(output, expected):
            # Get difference from expected length
            length_error = len(output) - len(expected)
            error_kind = ['long','short'][length_error < 0]
            # Fail test if argv not expected length
            msg = '''
The output {}
is {}er than
the expected {}
            '''.format(output, error_kind, expected)
            self.assertFalse(length_error, msg)

        # Value Error
        def same_list(output, expected):
            # Compare the output to expected output
            comparison = zip(output, expected)
            diff = [c[0] != c[1] for c in comparison]
            in_diff = enumerate(diff)
            # Get the first nonsame comparison
            wrong_n = next((i for i,d in in_diff if d), 0)
            # Fail test if not all same as expected
            msg = '''
Output item #{} is {}, but it should be {}
            '''.format(wrong_n, *comparison[wrong_n])
            self.assertFalse(any(diff), msg)

        # Test with Argv
        def test_one(test):
            args, keys = test['IN']
            # Send args and keys to to_argv
            output = bfly.UtilityLayer.to_argv(*args,**keys)
            # Check if the same length
            same_length(output, test['OUT'])
            # Check if the same list
            same_list(output, test['OUT'])

        # Run all TESTS in this class
        map(test_one, self.TESTS)

if __name__ == '__main__':
    ut.main()
