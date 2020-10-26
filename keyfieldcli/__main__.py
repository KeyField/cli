#!/usr/bin/env python3

import argparse
import sys

def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbosity increase"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Verbosity decrease"
    )
    subcmds = parser.add_subparsers(
        title="KeyField CLI Commands"
    )
    cmd_chat = subcmds.add_parser('chat', help="Send and receive messages with other users")
    cmd_search = subcmds.add_parser('search', help="Search for a User, Key, Device, or Homeserver")
    cmd_keys = subcmds.add_parser('keys', help="Manage KeyField keys")
    cmd_account = subcmds.add_parser('account', help="Manage your account on your homeserver")
    cmd_config = subcmds.add_parser('config', help="Change settings of the KeyField CLI")

    subcmds_chat = cmd_chat.add_subparsers(
        title="KeyField Chat Commands"
    )
    cmd_chat_send = subcmds_chat.add_parser('send', help="Send a message")
    cmd_chat_read = subcmds_chat.add_parser('read', help="Read messages received")
    cmd_chat_list = subcmds_chat.add_parser('list', help="List or search for chat channels")

    cmd_search.add_argument(
        'type',
        choices=['user', 'device', 'server', 'key'],
        help="Which type to search for"
    )
    cmd_search.add_argument(
        'search_text',
        help="Usernames, server names, server addresses, user keys, device names, device keys, etc..."
    )

    args = parser.parse_args()

if __name__ == '__main__':
    __main__()
