import dao


class RegisterService:
    _dao = dao.dao_service

    def register_client(self, name, public_key, aes_key):
        print(f"client {name} want to register")
        client = self._dao.get_client_by_name(name)
        if client:
            print(f"client {client.get_name()} already exists")
            # raise Exception(f"clien {name} already exists")
        else:
            self._dao.add_new_client(name, public_key, aes_key)
            print(f"client {name} added to DB")


if __name__ == "__main__":
    r = RegisterService()
    r.register_client("Super_Admin", "fdsfdsfds", "fsdfsd")
