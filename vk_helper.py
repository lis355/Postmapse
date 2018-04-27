#!/usr/bin/python3
# -*- coding: utf-8 -*-

from jsonf_python import jsonf
import namev

def get_account_info(provider, owner_id):
	user = provider.get("users.get", user_ids=owner_id)[0]
	return user


def get_self_account_info(provider):
	user = provider.get("users.get")[0]
	return user


def get_self_id(provider):
	return get_self_account_info(provider)["id"]


def get_rus_name(account_info):
	return "{0} {1}".format(account_info["first_name"], account_info["last_name"])


def get_eng_name(account_info):
	return namev.name(get_rus_name(account_info))
