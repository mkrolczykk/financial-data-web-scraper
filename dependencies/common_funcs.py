"""
Common functions
"""

try:
    import httplib
except:
    import http.client as httplib


def check_www_conn():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)

    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False


def serialize_json(data):
    def serialize(obj):
        if obj is None:
            return 'null'   # convert python None to json null
        elif isinstance(obj, dict):
            serialized_dict = '{'
            for key, value in obj.items():
                serialized_dict += f'"{key}": {serialize(value)}, '
            serialized_dict = serialized_dict.rstrip(', ')
            serialized_dict += '}'
            return serialized_dict
        elif isinstance(obj, list):
            serialized_list = '['
            for item in obj:
                serialized_list += serialize(item) + ', '
            serialized_list = serialized_list.rstrip(', ')
            serialized_list += ']'
            return serialized_list
        elif isinstance(obj, bool):
            return 'true' if obj else 'false'  # Serialize bool values to true or false
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return str(obj)

    return serialize(data)


def save_json(data, file_path):
    with open(file_path, 'w') as file:
        serialized_data = serialize_json(data)
        file.write(serialized_data)


def save_csv(data, file_path, headers):
    with open(file_path, 'w') as file:
        file.write(','.join(headers) + '\n')    # write headers
        for row in data:
            row_str = ','.join(map(str, row))
            file.write(row_str + '\n')