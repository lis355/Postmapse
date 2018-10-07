#!/usr/bin/python3
# -*- coding: utf-8 -*-

from jsonf_python import jsonf
import vk
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("credentials", type=str)
	parser.add_argument("username", type=str)
	parser.add_argument("password", type=str)
	parser.add_argument("v", type=str)
	parser.add_argument("-out", type=str, default="vk.token")
	line_args = parser.parse_args()

	credentials = jsonf.load(line_args.credentials)
	credentials["username"]= line_args.username
	credentials["password"] = line_args.password
	credentials["v"] = line_args.password

	token = vk.vk_api.request_token(credentials)

	# print(token)

	with open(line_args.out, "w", encoding="utf-8") as token_file:
		token_file.write(token)
