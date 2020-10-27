#!/usr/bin/env python3

import argparse
import sys

from .cmds import keys, chat, user

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
        title="KeyField CLI Commands",
    )
    cmd_chat = subcmds.add_parser('chat', help="Send and receive messages with other users")
    cmd_search = subcmds.add_parser('search', help="Search for a User, Key, Device, or Homeserver")
    cmd_keys = subcmds.add_parser('keys', help="Manage KeyField keys")
    cmd_account = subcmds.add_parser('account', help="Manage your account on your homeserver")
    cmd_config = subcmds.add_parser('config', help="Change settings of the KeyField CLI")
    cmd_user = subcmds.add_parser('user', help="Manage or view your user identity.")

    subcmds_keys = cmd_keys.add_subparsers(
        title="KeyField Key Management Commands",
        dest="command",
        required=True,
    )
    cmd_keys_newdevice = subcmds_keys.add_parser('newdevice', help="Initialize this machine as a KeyField device.")
    cmd_keys_newdevice.set_defaults(func=keys.new_device)
    cmd_keys_newdevice.add_argument('devicename', type=str, help="Public friendly name of the device.")
    cmd_keys_newdevice.add_argument('--force', action='store_true', help="Overwrite any existing device key.")
    cmd_keys_newuser = subcmds_keys.add_parser('newuser', help="Create a new KeyField identity.")
    cmd_keys_newuser.set_defaults(func=keys.new_user)
    cmd_keys_newuser.add_argument('username', type=str)
    cmd_keys_newuser.add_argument('--force', action='store_true', help="Overwrite the existing user identity.")
    cmd_keys_rotate = subcmds_keys.add_parser('rotate', help="Regenerate a new main user keypair, preserving previous keypairs.")
    cmd_keys_rotate.set_defaults(func=keys.rotate_user_key)

    subcmds_user = cmd_user.add_subparsers(
        title="KeyField User Identity Management Commands",
        dest="command",
        required=True
    )
    cmd_user_info = subcmds_user.add_parser('info', help="View information about the local user identity.")
    cmd_user_info.set_defaults(func=user.user_info)
    cmd_user_profile = subcmds_user.add_parser('profile', help="View the full public user identity block")
    cmd_user_profile.set_defaults(func=user.user_profile)
    cmd_user_profile.add_argument('--export', type=str, metavar='file', help="Write the signed binary profile data to a file. (Same data published to a homeserver)")

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

    if 'func' not in args:
        print(f"Command not yet implemented!")
        return

    args.func(args)

if __name__ == '__main__':
    __main__()
