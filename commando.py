#!/usr/bin/env python
# vim: sw=4: et:
import inspect
import sys
import string
import cmd
import new

class Commando(cmd.Cmd):

    def __init__(self, completekey='tab', stdin=sys.stdin, stdout=sys.stdout):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
    
# DECORATOR
class command(object):
    def __init__(self, name, prompts=()):
        self.name = name
	self.prompts = {}
        for argname, prompt, argtype in prompts:
            self.prompts[argname] = (prompt, argtype)

    def parseargs(self, argstr):
        """Args are separated by white-space or commas.  Unless a value is
        surrounded by single or double-quotes, white space will be trimmed.

        >>> parseargs('A B C')
        ("A", "B", "C")

        >>> parseargs('A, B, C')
        ("A", "B", "C")

        >>> parseargs('A ,, C')
        ("A", None, "C")

        >>> parseargs('"A " " B " C')
        ("A ", " B ", "C")
        """
        args = []
        def parser():
            while True:
                char = (yield)
                if char != ' ': 
                    arg_accumulator = []
                    if char != ',':
                        arg_accumulator.append(char)
                    while True:
                        char = (yield)
                        if char in (',', " ", None):
                            arg = "".join(arg_accumulator).strip()
                            if arg == "":
                                args.append(None)
                            else:
                                args.append(arg)
                            break
                        else:
                            arg_accumulator.append(char)

        p = parser()
        p.send(None) # Start up the coroutine
        for char in argstr:
            p.send(char)
        p.send(None)

        return args 

    def __call__(self, f):
        f_args, f_varargs, f_varkwargs, f_defaults = inspect.getargspec(f)
        if f_defaults != None:
            f_first_default_index = len(f_args) - len(f_defaults)
        else:
            f_first_default_index = None

        def wrapped_f(commando, argstr):
	    args = self.parseargs(argstr)
            vals = []

            for i in xrange(len(f_args)):
                try:
                    text, val_type = self.prompts[f_args[i]]
                except KeyError:
                    # No prompt was provided, so generate
                    # a default one
                    val_type = str
                    text = "Enter %s" % (f_args[i])
                if i < len(args):
                    # Attempt to convert the type
                    vals.append(val_type(args[i]))
                else:
                    # Treat bools as yes/no
                    if val_type == bool:
                        if f_first_default_index == None or i < f_first_default_index:
                            val = None
                            # Since there is no default, keep prompting until the user
                            # answers
                            while val == None:
                                input = raw_input(text + " Y/N: ")
                                if input.upper() in ("Y", "YES"):
                                    val = True
                                elif input.upper() in ("N", "NO"):
                                    val = False
                        else:
                            default = f_defaults[i - f_first_default_index]
                            if default == True:
                                val = raw_input(text + " [Y]/N: ")
                            elif default == False:
                                val = raw_input(text + " Y/[N]: ")
                            else:
                                raise ValueError

                            if val.strip() == "":
                                val = default
                            elif val.upper() in ("Y", "YES"):
                                val = True
                            elif val.upper() in ("N", "NO"):
                                val = False
                            else:
                                raise ValueError
                    else:
                        if f_first_default_index == None or i < f_first_default_index:
                            val = None
                            # Since there is no default, keep prompting until the user
                            # answers
                            while val == None:
                                input = raw_input(text + ": ")
                                if input.strip() != "":
                                    val = input
                        else:
                            default = f_defaults[i - f_first_default_index]
                            val = raw_input(text + " [%s]: " % (default))
                            if val.strip() == "":
                                val = default
                            else:
                                val = val_type(val)
                    vals.append(val)

            # Call the function
            f(*vals)

        # Inherit the docstring
        wrapped_f.__doc__ = f.__doc__

        f_name = "do_" + self.name
        setattr(Commando, f_name, new.instancemethod(wrapped_f, None, Commando))

	# Don't return the wrapped function, because we want
	# to be able to call the functions without the prompt logic
        return f
