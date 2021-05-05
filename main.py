#!/usr/bin/env python3
"""Testing script"""
from argparse import ArgumentParser
from yta_tftp import TFTPServer


def main():
    """Entry point when ran as a script"""
    server = TFTPServer()
    server.run()


if __name__ == "__main__":
    params = ArgumentParser(description="YTA TFTP Server")
    main()
