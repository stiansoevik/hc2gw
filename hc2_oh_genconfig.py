#!/usr/bin/python
import hc2gw
import argparse
import os
import re

hc2gw_cmd = os.path.dirname(os.path.realpath(__file__)) + "/hc2gw.py"

def get_authority_str(authority):
    return "--user " + authority["user"] + " --password " + authority["password"] + " --host " + authority["host"]

def get_device_info_list(authority):
    devices = hc2gw.get_devices(authority)
    rooms = hc2gw.get_rooms(authority)
    device_info=[]
    for dev in devices:
        id_str = str(dev["id"])
        room = [room for room in rooms if room["id"] == dev["roomID"]][0]
        room_str = room["name"].encode('ascii', errors='ignore').replace(" ", "")
        name_str = dev["name"].encode('ascii', errors='ignore').replace(" ", "")
        name_str = re.sub("[\W]+", "", name_str)
        item_str = "Hc2_" + room_str + "_" + name_str
        get_ch_str = "exec:command:hc2gw_get_" + id_str
        set_ch_str = "exec:command:hc2gw_set_" + id_str
        device_info.append({"id": id_str, "room": room_str, "name": name_str, "item": item_str, "get_ch": get_ch_str, "set_ch": set_ch_str})
    return device_info

def make_items(authority):
    for dev in get_device_info_list(authority):
        print("String " + dev["item"])
        print("String " + dev["item"] + "_get { channel=\"" + dev["get_ch"] + ":output\" }")
        print("String " + dev["item"] + "_set { channel=\"" + dev["set_ch"] + ":input\" }")
        print

def make_things(authority):
    for dev in get_device_info_list(authority):
        print("Thing " + dev["get_ch"] + " [command=\"" + hc2gw_cmd + " " + get_authority_str(authority) + " get_value " + dev["id"] + "\", interval=10]")
        print("Thing " + dev["set_ch"] + " [command=\"" + hc2gw_cmd + " " + get_authority_str(authority) + " set_value " + dev["id"] + " %2$s\", interval=0, autorun=true]")

def make_rules(authority):
    for dev in get_device_info_list(authority):
        print("rule \"Hc2_Update_" + dev["item"] + "\"")
        print("    when Item " + dev["item"] + "_get changed")
        print("then")
        print("    " + dev["item"] + ".postUpdate(" + dev["item"] + "_get.state)")
        print("end")
        print
        print("rule \"Hc2_Update_" + dev["item"] + "_set\"")
        print("    when Item " + dev["item"] + " changed")
        print("then")
        print("    " + dev["item"] + "_set.sendCommand(" + dev["item"] + ".state.toString)")
        print("end")
        print

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generate openHAB configuration files for HC2 devices.")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--host")
    subparsers = parser.add_subparsers(dest="type")
    subparsers.add_parser("items")
    subparsers.add_parser("things")
    subparsers.add_parser("rules")
    args = parser.parse_args()
    authority = { "user": args.user, "password": args.password, "host": args.host }

    if args.type == "items":
        make_items(authority)
    elif args.type == "things":
        make_things(authority)
    elif args.type == "rules":
        make_rules(authority)
