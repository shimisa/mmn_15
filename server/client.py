class Client:
    def __init__(self, id, name, public_key, last_seen, aes_key):
        self._id = id
        self._name = name
        self._public_key = public_key
        self._last_seen = last_seen
        self._aes_key = aes_key

    def __str__(self):
        return f"name: {self._name}, id: {self._id}, last_seen: {self._last_seen}"

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_public_key(self):
        return self._public_key

    def get_last_seen(self):
        return self._last_seen

    def get_aes_key(self):
        return self._aes_key


class File:
    def __init__(self, id, file_name, path_name, verified):
        self._id = id
        self._file_name = file_name
        self._path_name = path_name
        self._verified = verified

    def __str__(self):
        return f"_file_name: {self._file_name}, id: {self._id}, path_name: {self._path_name}"

    def get_id(self):
        return self._id

    def get_file_name(self):
        return self._file_name

    def get_path_name(self):
        return self._path_name

    def get_verified(self):
        return self._verified
