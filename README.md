# Postmapse-Python
Vk Help Query Library Python

You must have a token-file in your execution directory.
To generate token you need "credentials.json" file:

```javascript
{
	"client_id": ...,
	"client_secret": ...,
	"scope": ...
}
```

Then use vk_get_token to get "vk.token" file:

```javascript
python postmapse/vk_get_token.py "credentials.json" "USERNAME" "PASSWORD"
```

Example of use postmapse in your scripts:

```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from postmapse import vk
from postmapse import vk_helper

vk_provider = vk.vk_api()
self_account_info = vk_helper.get_self_account_info(vk_provider)
self_id = vk_helper.get_self_id(vk_provider)
self_name = vk_helper.get_rus_name(self_account_info)

print("{0} {1}".format(self_id, self_name))
```