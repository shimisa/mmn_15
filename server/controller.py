import base64

import dao
import crypto1


class Controller:
    STORED_FILES = "stored_files"
    NULL_TERMINATED = "0"
    SERVER_VERSION = "1"
    REGISTRATION_REQUEST = "12"
    PUBLIC_KEY_REQUEST = "13"
    LOGIN_REQUEST = "14"
    FILE_REQUEST = "15"
    VALID_CRC_REQUEST = "16"
    BAD_CRC_REQUEST = "17"
    FOUR_TIME_BAD_CRC_REQUEST = "18"
    REGISTRATION_SUCCESS = "20"
    REGISTRATION_FAILED = "21"
    PUBLIC_KEY_RECEIVED = "22"
    FILE_RECEIVED = "23"
    MSG_RECEIVED = "24"
    LOGIN_ACCEPT = "25"
    LOGIN_REJECT = "26"
    ERROR = "27"

    CLIENT_ID_SIZE = "16"
    ZERO_SIZE = "0"

    MIN_OF_VALID_REQUEST = 23
    END_OF_CLIENT_ID = 16
    END_OF_VERSION = 17
    END_OF_CODE = 19
    END_OF_PAYLOAD_SIZE = 23

    CLIENT_NAME_SIZE = PAYLOAD_SIZE = FILE_NAME_SIZE = 255
    FORMAT = "utf-8"

    _dao = dao.dao_service
    crypto_service = crypto1.Crypto()

    def handle_request(self, msg):
        request = self._parse_request(msg)
        code_request = request.code
        response = None
        match code_request:
            case self.REGISTRATION_REQUEST:
                response = self._handle_registration_request(request)
            case self.PUBLIC_KEY_REQUEST:
                response = self._handle_public_key_request(request)
            case self.LOGIN_REQUEST:
                response = self._handle_user_login(request)
            case self.FILE_REQUEST:
                response = self._handle_file_request(request)
            case self.VALID_CRC_REQUEST:
                response = self._handle_valid_crc_request(request)
            case self.BAD_CRC_REQUEST:
                response = self._handle_bad_crc_request(request)
            case self.FOUR_TIME_BAD_CRC_REQUEST:
                response = self._handle_four_time_bad_crc_request(request)
            case _:
                response = self._handle_not_valid_request(request)

        return response

    def _parse_request(self, msg):
        self.validate_request(msg)

        client_id = msg[: self.END_OF_CLIENT_ID]
        version = msg[self.END_OF_CLIENT_ID: self.END_OF_VERSION]
        code = msg[self.END_OF_VERSION: self.END_OF_CODE]
        payload_size = msg[self.END_OF_CODE: self.END_OF_PAYLOAD_SIZE]
        payload = msg[self.END_OF_PAYLOAD_SIZE:]
        request = _Request(client_id, version, code, payload_size, payload)
        return request

    def _handle_registration_request(self, request):
        payload = request.payload
        if not len(payload) == self.CLIENT_NAME_SIZE:
            print("client name not valid")
            return self._get_error_response()
        client_name = payload.split(self.NULL_TERMINATED, 1)[0]
        client = self._dao.get_client_by_name(client_name)
        if client is not None:  # username exists
            return _Response(self.SERVER_VERSION, self.REGISTRATION_FAILED, self.ZERO_SIZE, "")
        client_id = self._dao.add_new_client(client_name, "public_key", "aes_key")
        res_payload = client_id
        return _Response(self.SERVER_VERSION, self.REGISTRATION_SUCCESS, str(len(res_payload)), res_payload)

    def _handle_public_key_request(self, request):
        payload = request.payload
        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        client_name = payload[:self.CLIENT_NAME_SIZE].split(self.NULL_TERMINATED, 1)[0]
        public_key = payload[self.CLIENT_NAME_SIZE:]
        client = self._dao.get_client_by_name(client_name)
        if client is None:
            print("client not exists")
            return self._get_error_response()
        aes_key = self.crypto_service.generate_aes_key()
        encrypted_aes_key = self.crypto_service.encrypt(aes_key, public_key)
        s = ""
        s = s.join(map(chr, aes_key))
        res_payload = client.get_id() + s
        self._dao.update_client(client_name, public_key, aes_key)
        return _Response(self.SERVER_VERSION, self.PUBLIC_KEY_RECEIVED, str(len(res_payload)), res_payload)

    def _handle_user_login(self, request):
        payload = request.payload
        res_payload = ""
        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        client_name = payload.split(self.NULL_TERMINATED, 1)[0]
        client = self._dao.get_client_by_name(client_name)
        if client is None:  # username not exists
            return _Response(self.SERVER_VERSION, self.LOGIN_REJECT, str(len(res_payload)), res_payload)
        public_key = client.get_public_key()
        if public_key == "public_key":
            res_payload = client.get_id()
            return _Response(self.SERVER_VERSION, self.LOGIN_REJECT, str(len(res_payload)), res_payload)
        aes_key = self.crypto_service.generate_aes_key()
        encrypted_aes_key = self.crypto_service.encrypt(aes_key, public_key)
        s = ""
        s = s.join(map(chr, aes_key))
        res_payload = client.get_id() + s
        self._dao.update_client(client_name, public_key, aes_key)
        return _Response(self.SERVER_VERSION, self.LOGIN_ACCEPT, str(len(res_payload)), res_payload)

    def _handle_file_request(self, request):
        payload = request.payload
        client_id = request.client_id
        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        content_size = payload[: 4]
        padded_file_name = payload[4: 259]
        file_name = padded_file_name
        if file_name == "":
            file_name = "received_file.txt"
        else:
            file_name = file_name.split(self.NULL_TERMINATED, 1)[0]
        message_content = payload[259:]
        if not len(message_content) == int(content_size):
            print("message_content not valid")
            return self._get_error_response()
        path_name = f'{self.STORED_FILES}/{file_name}'
        client = self._dao.get_client_by_id(client_id)
        aes_list_rep = client.get_aes_key().strip('][').split(', ')
        int_aes_list_rep = [int(i) for i in aes_list_rep]
        aes_key = bytes(int_aes_list_rep)
        decrypted_content = self.crypto_service.aes_decrypt(aes_key, bytes(message_content, 'utf-8'))
        # cksum = self.crypto_service.crc(str(decrypted_content))
        cksum = self.crypto_service.crc(message_content.encode())
        cksum = str(cksum)[:4]
        try:
            with open(path_name, 'w') as p:
                # p.write(decrypted_content)
                p.write(message_content)
        except PermissionError:
            print(f"no permission to open file: {path_name}")
        file = self._dao.get_file_by_file_name(file_name)
        if file is None:
            self._dao.add_new_file(client_id, file_name, path_name)
        res_payload = client_id + content_size + padded_file_name + cksum
        return _Response(self.SERVER_VERSION, self.FILE_RECEIVED, str(len(res_payload)), res_payload)

    def _handle_valid_crc_request(self, request):
        payload = request.payload
        client_id = request.client_id
        file_name = payload[: self.PAYLOAD_SIZE]
        file_name = file_name.split(self.NULL_TERMINATED, 1)[0]

        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        file = self._dao.get_file_by_file_name(file_name)
        if file is None:
            print("file not exists")
            return self._get_error_response()
        self._dao.update_file_valid_crc(file_name)
        res_payload = client_id
        return _Response(self.SERVER_VERSION, self.MSG_RECEIVED, str(len(res_payload)), res_payload)

    def _handle_bad_crc_request(self, request):
        payload = request.payload
        client_id = request.client_id
        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        file_name = payload[: self.PAYLOAD_SIZE]
        file_name = file_name.split(self.NULL_TERMINATED, 1)[0]
        file = self._dao.get_file_by_file_name(file_name)
        if file is None:
            print("file not exists")
            return self._get_error_response()
        res_payload = client_id
        return _Response(self.SERVER_VERSION, self.MSG_RECEIVED, str(len(res_payload)), res_payload)

    def _handle_four_time_bad_crc_request(self, request):
        payload = request.payload
        client_id = request.client_id
        if not len(payload) == int(request.payload_size):
            print("payload not valid")
            return self._get_error_response()
        file_name = payload[: self.PAYLOAD_SIZE]
        file_name = file_name.split(self.NULL_TERMINATED, 1)[0]
        file = self._dao.get_file_by_file_name(file_name)
        if file is None:
            print("file not exists")
            return self._get_error_response()
        res_payload = client_id
        return _Response(self.SERVER_VERSION, self.MSG_RECEIVED, str(len(res_payload)), res_payload)

    def _handle_not_valid_request(self, request):
        return self._get_error_response()

    def validate_request(self, msg):
        if len(msg) < self.MIN_OF_VALID_REQUEST and len(msg) != 0:
            raise Exception("request not valid")

    def _get_error_response(self):
        return _Response(self.SERVER_VERSION, self.ERROR, self.NULL_TERMINATED, self.NULL_TERMINATED)


class _Request:

    def __init__(self, client_id, version, code, payload_size, payload):
        self.client_id = client_id
        self.version = version
        self.code = code
        self.payload_size = payload_size
        self.payload = payload


class _Response:

    def __init__(self, version, code, payload_size, payload):
        self.version = version
        self.code = code
        self.payload_size = self._padd_to_four(payload_size)
        self.payload = payload

    def get_string_res(self):
        return self.version + self.code + self.payload_size + self.payload

    def __str__(self):
        return f"version: {self.version}, code: {self.code}, payload_size: {self.payload_size}, payload: {self.payload}"

    def _padd_to_four(self, payload_size):
        str = payload_size
        while len(str) < 4:
            str = "0" + str
        return str

    def _padd_file_name(self, payload_size):
        str = payload_size
        while len(str) < self.FILE_NAME_SIZE:
            str = str + "0"
        return str

