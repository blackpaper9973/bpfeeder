def deep_extend(*args):
    result = None
    for arg in args:
        if isinstance(arg, dict):
            if not isinstance(result, dict):
                result = {}
            for key in arg:
                result[key] = deep_extend(result[key] if key in result else None, arg[key])
        else:
            result = arg
    return result

def find_key_by_value(dic, val):
    for key, value in dic.items():
        if val == value:
            return key
    return "key doesn't exist"