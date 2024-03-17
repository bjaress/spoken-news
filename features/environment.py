import os
import time
import requests
import logging

from types import SimpleNamespace

def before_all(context):
    prop = SimpleNamespace()
    for key, value in os.environ.items():
        if key.startswith("prop."):
            include_in(prop, key.split(".")[1:], value)
    context.prop = prop


def include_in(namespace, key_path, value):
    as_dict = namespace.__dict__
    first = key_path[0]
    if len(key_path) == 1:
        as_dict[first] = value
    else:
        if first not in as_dict:
            as_dict[first] = SimpleNamespace()
        include_in(as_dict[first], key_path[1:], value)
