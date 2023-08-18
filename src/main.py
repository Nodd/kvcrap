#!/usr/bin/env python3
"""Basic wrapper to start the crapette game."""

import sys

if __name__ == "__main__":
    # Workaround : do not let kivy use the command line arguments
    # To be done before the following import
    args = sys.argv[1:]
    sys.argv = sys.argv[:1]

    from crapette.crapette import main

    main(args)
