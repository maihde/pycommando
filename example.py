#!/usr/bin/env python
# vim: sw=4: et:
import readline
import sys
from commando import *

# Define a command called "action1"
@command("action1")
def action1():
    """Do something"""
    print "action1"

# Define a command called "doit"
@command("doit", prompts=(("value2", "Enter a number", int),
                          ("value1", "Enter a string", str)))
def action2(value1, value2=5):
    """Do something else"""
    print "action2", repr(value1), repr(value2)

# Define a command called "go" using default prompts
@command("go")
def action3(value1=False):
    """Do another thing"""
    print "action3", repr(value1)

# Define multiple commands that call the same function
@command("exit")
@command("quit")
def exit():
    """Quit"""
    sys.exit(0)

commando = Commando()
commando.cmdloop()
