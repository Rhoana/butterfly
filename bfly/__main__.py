from Butterfly import Butterfly
import sys

def bfly():
    """ Makes the :class:`bfly.Butterfly` that does everything.
    Type ``bfly`` in a shell after ``bfly`` installed_.

    |bfly_help|
    """
    # Start the butterfly
    Butterfly(sys.argv)

if __name__ == "__main__":
    # Starts bfly on main
    bfly()
