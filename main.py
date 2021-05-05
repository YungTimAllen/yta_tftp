#!/usr/bin/env python3
"""x"""
from argparse import ArgumentParser
from yta_tftp import TFTPServer


def main(parser):
    """x"""
    server = TFTPServer()
    server.run()


if __name__ == "__main__":
    params = ArgumentParser(description="YTA TFTP Server")
    main(params.parse_args())
