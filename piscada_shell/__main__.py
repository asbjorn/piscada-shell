import cmd
import sys
from getpass import getpass
from concurrent.futures import CancelledError
from time import sleep
from itertools import cycle

# import requests
import piscada_shell


def progress_marker_while_future(fut):
    for frame in cycle(r'-\|/-\|/'):
        if not fut.running():
            print() # newline
            return
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.2)


class PiscadaShell(cmd.Cmd):
    into = 'Welcome to Piscada Shell. Type help or ? to list commands.\n'
    prompt = '> '
    auth_credentials = None
    controllers = None

    def do_auth_tokens(self, arg):
        if self.auth_credentials is None:
            print("Need to login first")
            return

        access_tokens = self.auth_credentials.get('accessTokens', {})
        for k, v in access_tokens.items():
            print(f"key={k} -> value={v}")


    def do_login(self, arg):
        """Login to Piscada API - retrieve access tokens needed to call APIs"""
        print(f"Login..")
        username = input('Username: ')
        password = getpass('Password: ')

        # retval = piscada_shell.login(username, password)
        # if retval is None:
        #     print("Unable to login! Maybe wrong username and/or password?")
        #     return
        fut = piscada_shell.login(username, password)

        progress_marker_while_future(fut)
        if fut.cancelled():
            print("Login cancelled")
        elif fut.done():
            try:
                result = fut.result()
                print(f"Login result: {result}")
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


    def do_list_controllers(self, arg):
        """List Piscada controllers assigned to your account.
        The result will be cached. To force a update append the '-u'
        or '--update':

        i.e. > list_controllers -u
        """
        if self.auth_credentials is None:
            print("Login before calling any API calls..")
            return

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

    def do_logout(self, arg):
        self.prompt = '> '
        self.auth_credentials = None

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    PiscadaShell().cmdloop('Welcome to Piscada Shell.. Type help or ?')
