#!/usr/bin/python
import argparse
import logging
import requests
import sys

#logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def send_hc2_api(verb, path, post_data=None):
    url = "http://" + user + ":" + password + "@" + host + "/api" + path
    logging.info(verb + " " + url)
    if post_data:
        logging.debug(post_data)
    
    if verb == "GET":
        r = requests.get(url)
    if verb == "POST":
        r = requests.post(url, data = post_data)
    
    logging.debug(r.text)
    return r.json()
    
def set_value(id, value):
    path = "/devices/" + str(id) + "/action/setValue"
    payload = " { \"args\" : [" + str(value) + "] }"
    send_hc2_api("POST", path, payload)

def get_value(id):
    response = send_hc2_api("GET", "/devices/" + str(id))
    if "properties" in response:
        if "value" in response["properties"]:
            return response["properties"]["value"]
        else:
            logging.warning("No value for device " + str(id))
            return "N/A"
    else:
        logging.warning("No properties for device " + str(id))
        return "N/A"

def get_devices():
    response = send_hc2_api("GET", "/devices")
    logging.debug(response)

    real_devices = [device for device in response if device["roomID"] != 0]
    return real_devices

def print_devices():
    for d in get_devices():
        print("[" + str(d["id"]) + "]" +
              " @" + str(d["roomID"]) +
              " \"" + d["name"] + "\"" +
              " = " + get_value(d["id"])
              )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Control Fibaro HC2.")
    parser.add_argument("--host", required = True)
    parser.add_argument("--user", required = True)
    parser.add_argument("--password", required = True)
    subparsers = parser.add_subparsers(dest="command")
    
    parser_set_value = subparsers.add_parser("set_value")
    parser_set_value.add_argument("id", type = int)
    parser_set_value.add_argument("value", type = int)
    
    parser_get_value = subparsers.add_parser("get_value")
    parser_get_value.add_argument("id", type = int)
    
    parser_get_devices = subparsers.add_parser("print_devices")
    
    parser_make_oh_items = subparsers.add_parser("make_oh_items")
    parser_make_oh_things = subparsers.add_parser("make_oh_things")
    parser_make_oh_sitemap = subparsers.add_parser("make_oh_sitemap")

    args = parser.parse_args()
    
    host = args.host
    user = args.user
    password = args.password
    
    if args.command == "set_value":
        set_value(args.id, args.value)
    elif args.command == "get_value":
        value = get_value(args.id)
        print(str(value))
    elif args.command == "print_devices":
        print_devices()