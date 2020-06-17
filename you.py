#!/usr/bin/env python3

"""
Example config:

youtrack:
    host: "https://youtrack.pondus.de"
    username: greune
    password: XXX

aliases:
    easy: "sprint: {April19 A} project: BON #easy #unresolved"
"""

import sys
import os

from copy import copy
from yaml import load, FullLoader

from youtrack.connection import Connection

def get_config_variables(config):
    config_variables = []
    for variable in config.get("variables", {}).keys():
        value = config["variables"][variable]
        variable = "${%s}" % variable
        config_variables.append((variable, value))
    return config_variables


bold = "\033[1m"
italic = "\033[3m"
purple = "\033[95m"
grey = "\033[90m"
yellow = "\033[33m"
cyan = "\033[36m"
green = "\033[92m"
reset = "\033[0m"


def convert_ticket_state_to_icon(state):
    if state == "Fertig":
        return green + "✔" + reset
    if state == "Umgesetzt":
        return green + "(✔)" + reset
    if state == "In Entwicklung":
        return yellow + "🔧 " + reset
    if state == "In Test":
        return cyan + "🔎 " + reset
    if state == "Neu":
        return cyan + "💫 " + reset
    if state == "Eingeplant":
        return cyan + "🥅 " + reset
    return state

def is_blocked_tag_to_icon(tags):
    if tags is not None and "Blockade" in tags:
        return "🛑"
    else:
        return "  "


# check that cli arguments were supplied
if len(sys.argv) <= 1:
    print("Usage: you <QUERY/ALIAS>")
    exit(1)

## load config and connection details
config_path = os.path.expanduser("~/.youtrack.yml")

argv = copy(sys.argv)
argv.pop(0)

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = load(f, Loader=FullLoader)
    instance = config["youtrack"]["host"]
    username = config["youtrack"]["username"]
    password = config["youtrack"]["password"]
else:
    raise Exception("config file under '%s' not found" % config_path)

# use e.g. ${sprint} in query, which gets replaced to the current sprint name
# dyn_variables = [("${sprint}", "{April19 B}")]
dyn_variables = get_config_variables(config)


## check if we only should list aliases
if config is not None and argv[0] == "aliases":
    for alias in config.get("aliases", {}).keys():
        print(alias)
    exit(0)

## check if alias is used
if config is not None and "aliases" in config:
    provided_alias = [alias for alias in config["aliases"].keys() if alias == argv[0]]
    if len(provided_alias) > 0:
        filter_query = config["aliases"][provided_alias[0]]
    else:
        filter_query = " ".join(sys.argv[1:])
else:
    filter_query = " ".join(sys.argv[1:])

# replace dyn_variables in filter_query
for v, value in dyn_variables:
    filter_query = filter_query.replace(v, value)

print(grey, "filter_query:", filter_query, reset)

connection = Connection(instance, username, password)

## print found issues
for issue in connection.get_all_issues(filter_query, 0, 100):
    # print(issue.to_xml)
    projectShortName = issue.get("projectShortName", None)
    numberInProject = issue.get("numberInProject", None)
    issue_number = "%s-%s" % (projectShortName, numberInProject)
    summary = issue.get("summary", None)
    blocked_icon = is_blocked_tag_to_icon(issue.tags)
    state = convert_ticket_state_to_icon(issue.get("State", None))
    print(state + blocked_icon, end="")
    print(bold, green, issue_number, reset, summary, end="")
    if issue.tags is not None:
        print(" ", italic, purple, issue.tags, reset)
    else:
        print()

