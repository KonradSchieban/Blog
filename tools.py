import hmac

SECRET = 'hsajdfkhjkasdlghjsdfgmdsngjsdhfg'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

