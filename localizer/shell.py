import logging
import os
import pprint
from cmd import Cmd
from distutils.util import strtobool

import localizer
from localizer import wifi, capture, params

logger = logging.getLogger('localizer')
_file_logger = logging.FileHandler('localizer.log')
_file_logger.setLevel(logging.DEBUG)
_file_logger.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s'))
logger.addHandler(_file_logger)
logger.info("****STARTING LOCALIZER****")

# Helper class for exit functionality
class ExitCmd(Cmd):
    @staticmethod
    def can_exit():
        return True

    def onecmd(self, line):
        r = super(ExitCmd, self).onecmd(line)
        if r and (self.can_exit() or input('exit anyway ? (yes/no):') == 'yes'):
            return True
        return False

    @staticmethod
    def do_exit(args):
        """Exit the interpreter."""
        return True

    @staticmethod
    def do_quit(args):
        """Exit the interpreter."""
        return True


# Helper class for shell command functionality
class ShellCmd(Cmd, object):
    @staticmethod
    def do_shell(s):
        """Execute shell commands in the format 'shell <command>'"""
        os.system(s)


# Base Localizer Shell Class
class LocalizerShell(ExitCmd, ShellCmd):

    def __init__(self):
        super(LocalizerShell, self).__init__()

        self._modules = ["antenna", "gps", "capture", "wifi"]

        # Ensure we have root
        if os.getuid() != 0:
            print("Error: this application needs root to run correctly. Please run as root.")
            exit(1)

        # WiFi
        logger.info("Initializing WiFi")
        # Set interface to first
        iface = wifi.get_first_interface()
        if iface is not None:
            localizer.params.iface = iface
        else:
            logger.error("No valid wireless interface available")
            exit(1)

        # Start the command loop - these need to be the last lines in the initializer
        self._update_prompt()
        self.cmdloop('Welcome to Localizer Shell...')

    def do_debug(self, args):
        """
        Sets printing of debug information or shows current debug level if no param given

        :param args: (Optional) Set new debug value.
        :type args: str
        """

        args = args.split()
        if len(args) > 0:
            try:
                val = strtobool(args[0])
                localizer.set_debug(val)
            except ValueError:
                logger.error("Could not understand debug value '{}'".format(args[0]))

        print("Debug is '{}'".format(localizer.debug))

    def complete_test(self, text, line, begidx, endidx):
        return [i for i in self._modules if i.startswith(text)]

    def do_set(self, args):
        """
        Set a named parameter.

        :param args: Parameter name followed by new value
        :type args: str
        """

        split_args = args.split()
        if len(split_args) < 1:
            logger.error("You must provide at least one argument".format(args))
        elif len(split_args) == 1:
            if split_args[0] == "iface":
                iface = wifi.get_first_interface()

                if iface is not None:
                    localizer.params.iface = iface
                else:
                    logger.error("There are no wireless interfaces available.")
            else:
                logger.error("Parameters require a value".format(split_args[0]))
        elif split_args[0] in params.VALID_PARAMS:
            try:
                param = split_args[0]
                value = split_args[1]
                # Validate certain parameters
                if split_args[0] == "iface":
                    localizer.params.iface = value
                elif param == "duration":
                    localizer.params.duration = value
                elif param == "degrees":
                    localizer.params.degrees = value
                elif param == "bearing":
                    localizer.params.bearing = value
                elif param == "hop_int":
                    localizer.params.hop_int = value
                elif param == "path":
                    localizer.params.path = value
                elif param == "test":
                    localizer.params.test = value

                print("Parameter '{}' set to '{}'".format(param, value))

            except ValueError as e:
                logger.error(e)
        else:
            logger.error("Invalid parameter '{}'".format(split_args[0]))

        self._update_prompt()

    def do_get(self, args):
        """
        View the specified parameter or all parameters if none specified. May also view system interface data

        :param args: param name, ifaces for system interfaces, or blank for all parameters
        :type args: str
        """

        split_args = args.split()

        if len(split_args) >= 1:
            if split_args[0] == "ifaces":
                pprint.pprint(wifi.get_interfaces())
            elif split_args[0] == "params":
                print(str(localizer.params))
            else:
                logger.error("Unknown parameter '{}'".format(split_args[0]))
        else:
            pprint.pprint(wifi.get_interfaces())
            print(str(localizer.params))

    def do_capture(self, args):
        """
        Start the capture with the needed parameters set

        :param args: No parameter needed, but required parameters must be set using the `set` command
        :type args: str
        """

        if not localizer.params.validate():
            logger.error("You must set 'iface' and 'duration' parameters first")
        else:
            cap = capture.Capture()
            cap.capture()

    def _update_prompt(self):
        """
        Update the command prompt based on the iface and duration parameters
        """

        elements = []
        if localizer.params.test is not None:
            test = (localizer.params.test[:7] + '..') if len(localizer.params.test) > 9 else localizer.params.test
            elements.append(localizer.G + test)
        if localizer.params.iface is not None:
            elements.append(localizer.C + localizer.params.iface)
        if localizer.params.duration > 0:
            elements.append(localizer.GR + str(localizer.params.duration) + 's')

        separator = localizer.W + ':'
        self.prompt = separator.join(elements) + localizer.W + '> '

    def emptyline(self):
        pass
