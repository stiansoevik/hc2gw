#!/usr/bin/python
import argparse
import logging
import requests
import sys

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

def send_hc2_api(verb, authority, path, post_data=None):
    url = "http://" + authority + "/api" + path
    logging.info(verb + " " + url)
    if post_data:
        logging.debug(post_data)
    
    if verb == "GET":
        r = requests.get(url)
    if verb == "POST":
        r = requests.post(url, data = post_data)
    
    logging.debug(r.text)
    return r.json()
    
def set_value(authority, id, value):
    path = "/devices/" + str(id) + "/action/setValue"
    payload = " { \"args\" : [" + str(value) + "] }"
    send_hc2_api("POST", authority, path, payload)

def get_value(authority, id):
    response = send_hc2_api("GET", authority, "/devices/" + str(id))
    if "properties" in response:
        if "value" in response["properties"]:
            return response["properties"]["value"]
        else:
            logging.warning("No value for device " + str(id))
            return "N/A"
    else:
        logging.warning("No properties for device " + str(id))
        return "N/A"

def get_devices(authority):
    response = send_hc2_api("GET", authority, "/devices")
    logging.debug(response)

    real_devices = [device for device in response if device["roomID"] != 0]
    return real_devices

def get_rooms(authority):
    response = send_hc2_api("GET", authority, "/rooms")
    logging.debug(response)

    return response

def print_devices(authority):
    for d in get_devices(authority):
        print("[" + str(d["id"]) + "]" +
              " @" + str(d["roomID"]) +
              " \"" + d["name"] + "\"" +
              " = " + get_value(d["id"])
              )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Control Fibaro HC2.")
    parser.add_argument("authority", help = "user, password and host part of URL (defined as authority) to Fibaro HC2. Example: admin:1234@192.168.1.100")
    subparsers = parser.add_subparsers(dest="command")
    
    parser_set_value = subparsers.add_parser("set_value")
    parser_set_value.add_argument("id", type = int)
    parser_set_value.add_argument("value", type = int)
    
    parser_get_value = subparsers.add_parser("get_value")
    parser_get_value.add_argument("id", type = int)
    
    parser_get_devices = subparsers.add_parser("print_devices")
    
    args = parser.parse_args()
    
    if args.command == "set_value":
        set_value(args.authority, args.id, args.value)
    elif args.command == "get_value":
        value = get_value(args.authority, args.id)
        print(str(value))
    elif args.command == "print_devices":
        print_devices(args.authority)
