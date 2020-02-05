from typing import List

import sys
import loxmain


def main() -> None:
    """ Main function
        Get arguments and run interpreter """

    try:
        args: List[str] = list(sys.argv)
        loxmain.Lox(args[1:])
    except SystemExit as e:
        print("System Exit: ", e.code)


if __name__ == '__main__':
    main()
