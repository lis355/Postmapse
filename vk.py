#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
from jsonf_python import jsonf
import os
import time
from argparse import Namespace as ndict
import requests


class vk_api(object):
	__k_count = 100
	__k__token_path = "vk.token"
	__k__sleep_sec = 0.25

	__k_server_success_responce_status = 200
	__k_server_errors = \
		{
			0: "UNKNOWN",
			400: "BAD_REQUEST",
			401: "UNAUTHORIZED",
			403: "FORBIDDEN",
			404: "NOT_FOUND",
			420: "FLOOD",
			500: "INTERNAL"
		}

	@staticmethod
	def md5(s):
		h = hashlib.md5()
		h.update(s.encode("utf-8"))
		return h.hexdigest()

	def __load_hash(self):
		self.__hash.clear()
		if not os.path.isdir(self.__k_hash_dir):
			os.mkdir(self.__k_hash_dir)

		for file_path_dir in os.listdir(self.__k_hash_dir):
			file_path = self.__k_hash_dir + file_path_dir
			key = os.path.splitext(os.path.basename(file_path))[0]
			self.__hash[key] = jsonf.load(file_path)

	def __save_hash(self, s, request):
		if not os.path.isdir(self.__k_hash_dir):
			os.mkdir(self.__k_hash_dir)

		file_path = self.__k_hash_dir + s + ".json"
		jsonf.save(request, file_path)

	def clear_hash(self):
		for file_path_dir in os.listdir(self.__k_hash_dir):
			file_path = self.__k_hash_dir + file_path_dir
			os.remove(file_path)

		os.rmdir(self.__k_hash_dir)

		self.__hash = {}

	def __init__(self, version):
		self.version = version
		self.__token = ""
		self.__first_get = False
		self.__k_hash_dir = os.getcwd() + "/vk_debug_hash/"
		self.__hash = {}

		self.debug = True
		self.__load_hash()

	@staticmethod
	def __get_request(request_str):
		return requests.get(request_str)

	@staticmethod
	def __create_request_string(method, params) -> str:
		params_string = "".join(["&{0}={1}".format(param_key, params[param_key]) for param_key in sorted(params)])
		return method + params_string

	@property
	def token(self) -> str:
		if not self.__token:
			if os.path.isfile(vk_api.__k__token_path):
				with open(vk_api.__k__token_path, "r", encoding="utf-8") as token_file:
					self.__token = token_file.read()
		return self.__token

	@staticmethod
	def request_token(params) -> str:
		params["grant_type"] = "password"
		request_string = vk_api.__create_request_string("https://oauth.vk.com/token?", params)

		request = vk_api.__get_request(request_string)
		request_content = request.json()
		token = request_content["access_token"]
		return token

	@staticmethod
	def __clear_token(self):
		if os.path.isfile(vk_api.__k__token_path):
			os.remove(vk_api.__k__token_path)
		self.__token = ""

	def __get_string_request(self, request_string):
		if not self.__first_get:
			self.__first_get = True
		else:
			time.sleep(vk_api.__k__sleep_sec)

		request = vk_api.__get_request(request_string)
		if request.status_code != vk_api.__k_server_success_responce_status:
			status_code = request.status_code
			if status_code not in vk_api.__k_server_errors:
				status_code = 0

			raise Exception("Server error {0} {1}".format(status_code, vk_api.__k_server_errors[status_code]))

		request_json = request.json()
		if "error" in request_json:
			request_json_error = request_json["error"]
			if request_json_error:
				raise Exception("Bad request: error {0}. {1}".format(request_json_error["error_code"], request_json_error["error_msg"]))
		else:
			return request_json["response"]

	def get(self, method, **kwargs):
		rargs = dict(kwargs)
		rargs["access_token"] = self.token
		rargs["v"] = self.version
		request_string = vk_api.__create_request_string("https://api.vk.com/method/{0}?".format(method), rargs)

		if self.debug:
			key = vk_api.md5(request_string)
			if key in self.__hash:
				request_content = self.__hash[key]
			else:
				request_content = self.__get_string_request(request_string)
				self.__hash[key] = request_content
				self.__save_hash(key, request_content)
		else:
			request_content = self.__get_string_request(request_string)

		return request_content

	def chain_items(self, *args, **kwargs) -> ndict:
		k_count_s = "count"
		k_items_s = "items"

		max_count = 0
		has_limit = k_count_s in kwargs
		if has_limit:
			max_count = kwargs[k_count_s]
			del kwargs[k_count_s]

		start_count = vk_api.__k_count if has_limit and max_count > vk_api.__k_count else max_count

		offset = 0
		json_response = self.get(*args, **kwargs, offset=offset, count=start_count)

		if k_count_s not in json_response:
			return ndict(json=json_response, items=[])

		total_count = json_response[k_count_s]
		count = min(total_count, max_count) if has_limit else total_count

		result = json_response[k_items_s]
		offset += len(result)

		while offset < count:
			next_count = min(vk_api.__k_count, count - offset)
			next_json = self.get(*args, **kwargs, offset=offset, count=next_count)
			# print("{0}".format(offset / count))

			if k_items_s not in next_json:
				break

			next_result = next_json[k_items_s]
			next_result_length = len(next_result)
			offset += next_result_length
			result.extend(next_result)

			if next_result_length == 0:
				break

		return ndict(json=json_response, items=result)
