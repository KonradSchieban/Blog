from tools import *
# implement the function make_salt() that returns a string of 5 random
# letters use python's random module.
# Note: The string package might be useful here.

SECRET = "This is a secret"

cookie = make_secure_val("hell")
print cookie

print check_secure_val(cookie)
print check_secure_val(cookie + "asdf")