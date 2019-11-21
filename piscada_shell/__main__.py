import cmd
import sys
from getpass import getpass
from concurrent.futures import CancelledError
from time import sleep
from itertools import cycle
import functools
from colorama import init, Fore, Back, Style
from pprint import pprint

import piscada_shell

init()



def progress_marker_while_future(fut):
    for frame in cycle(r'-\|/-\|/'):
        if not fut.running():
            print() # newline
            return
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.2)


def authenticated(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        s = args[0]
        if s.auth_credentials is None:
            print(Fore.RED + "Need to login first" + Fore.RESET)
            return
        return func(*args, **kwargs)
    return wrapper


class PiscadaShell(cmd.Cmd):
    into = Fore.CYAN + 'Welcome to Piscada Shell. Type help or ? to list commands.\n' + Fore.RESET
    prompt = Fore.CYAN + '> ' + Fore.RESET
    auth_credentials = None
    controllers = None

    @authenticated
    def do_auth_tokens(self, arg):
        access_tokens = self.auth_credentials.get('accessTokens', {})
        pprint(access_tokens)


    def do_login(self, arg):
        """Login to Piscada API - retrieve access tokens needed to call APIs"""
        username = input(Fore.WHITE + Style.DIM + 'Enter username: ' + Style.NORMAL + Fore.RESET)
        password = getpass(Fore.WHITE + Style.DIM + 'Password: ' + Style.NORMAL + Fore.RESET)

        fut = piscada_shell.login(username, password)
        progress_marker_while_future(fut)
        if fut.cancelled():
            print(Fore.RED + "Login cancelled" + Fore.RESET)
        elif fut.done():
            try:
                result = fut.result()
                # print(f"Login result: {result}")
                if result.ok:
                    retval = result.json()
                    self.auth_credentials = retval
                    access_tokens = self.auth_credentials.get('accessTokens', {})
                    services = ", ".join(access_tokens.keys())
                    print(f"Gained tokens for: {services}")

                    self.user = username
                    self.prompt = f'[{self.user}]> '
                else:
                    print("Unable to login! Maybe wrong username and/or password?")
                    return
            except CancelledError as err:
                print(f"cancellederror: {err}")


    @authenticated
    def do_list_controllers(self, arg):
        """List Piscada controllers assigned to your account.
        The result will be cached. To force a update append the '-u'
        or '--update':

        i.e. > list_controllers -u
        """
        force_update = False
        if "-u" in arg or "--update" in arg:
            force_update = True


        if self.controllers is None or force_update:
            access_tokens = self.auth_credentials.get('accessTokens', {})
            controllers_token = access_tokens.get('controllers-api.piscada.cloud')
            fut = piscada_shell.list_controllers(controllers_token)

            progress_marker_while_future(fut)
            if fut.cancelled():
                print("Action cancelled")
                return

            try:
                result = fut.result()
                print(f"Result: {result}")
                if result.ok:
                    retval = result.json()
                    self.controllers = retval.get('data')
                else:
                    print(f"Response NOT ok.. {result.status_code} {result.content}")
            except CancelledError as err:
                print(f"cancellederror: {err}")

        for ctrl in self.controllers:
            print(f"Id: {ctrl['uuid']}")
            print(f"Name: {ctrl['name']}")
            print(f"Hostname: {ctrl['hostname']}")
            print()

    @authenticated
    def do_controller_tag_timeseries(self, arg):
        """Output tag timeseries for the the chosen controller. Might change this to be more user friendly.

        usage: controller_tag_timeseries CONTROLLER_ID TAG_NAME
        """
        args = arg.split(" ")
        if len(args) < 2:
            print("Usage: controller_tag_timeseries CONTROLLER_ID TAG_NAME")
            return
        controller = args[0]
        tag_name = args[1]

        access_tokens = self.auth_credentials.get('accessTokens', {})
        historian_token = access_tokens.get('historian.piscada.cloud')
        fut = piscada_shell.tag_timeseries(historian_token, controller, tag_name)

        progress_marker_while_future(fut)
        if fut.cancelled():
            print("Action cancelled")
            return

        try:
            result = fut.result()
            print(f"Result: {result}")
            if result.ok:
                retval = result.json()
                print(retval)
            else:
                print(f"Response NOT ok.. {result.status_code} {result.content}")
        except CancelledError as err:
            print(f"cancellederror: {err}")

    def do_logout(self, arg):
        self.prompt = '> '
        self.auth_credentials = None

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    PiscadaShell().cmdloop('Welcome to Piscada Shell.. Type help or ?')
