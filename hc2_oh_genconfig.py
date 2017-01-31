#!/usr/bin/python
import hc2gw
import argparse
import os
hc2gw_cmd = os.path.dirname(os.path.realpath(__file__)) + "/hc2gw.py"

def get_device_info_list(authority):
    devices = hc2gw.get_devices(authority)
    rooms = hc2gw.get_rooms(authority)
    device_info=[]
    for dev in devices:
        id_str = str(dev["id"])
        room = [room for room in rooms if room["id"] == dev["roomID"]][0]
        room_str = room["name"].encode('ascii', errors='ignore').replace(" ", "")
        name_str = dev["name"].encode('ascii', errors='ignore').replace(" ", "")
        get_ch_str = "exec:command:hc2gw_get_" + id_str
        set_ch_str = "exec:command:hc2gw_set_" + id_str
        device_info.append({"id": id_str, "room": room_str, "name": name_str, "get_ch": get_ch_str, "set_ch": set_ch_str})
    return device_info

def make_items(authority):
    for dev in get_device_info_list(authority):
        item_name = ("Hc2_" + dev["room"] + "_" + dev["name"])
        print ("String " + item_name + "_get { channel=\"" + dev["get_ch"] + ":output\" }")
        print ("String " + item_name + "_set { channel=\"" + dev["set_ch"] + ":input\" }")

def make_things(authority):
    for dev in get_device_info_list(authority):
        print ("Thing " + dev["get_ch"] + " [command=\"" + hc2gw_cmd + " " + authority + " get_value " + dev["id"] + "\", interval=10]")
        print ("Thing " + dev["set_ch"] + " [command=\"" + hc2gw_cmd + " " + authority + " set_value " + dev["id"] + " %2$s\", interval=0, autorun=true]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generate openHAB configuration files for HC2 devices.")
    parser.add_argument("authority", help = "user, password and host part of URL (defined as authority) to Fibaro HC2. Example: admin:1234@192.168.1.100")
    subparsers = parser.add_subparsers(dest="type")
    subparsers.add_parser("items")
    subparsers.add_parser("things")
    args = parser.parse_args()

    if args.type == "items":
        make_items(args.authority)
    elif args.type == "things":
        make_things(args.authority)