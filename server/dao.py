import sqlite3
import config
import client
import uuid
import datetime
import shortuuid


class _Dao:

    def __init__(self):
        print("Dao class initiated")
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(config.database.get("db_path"))
        print("connected to database successfully")
        return conn

    def _close(self, conn):
        conn.close()
        print("disconnected database")

    def _init_db(self):
        conn = self._connect()
        conn.execute("""DROP TABLE files;""")
        conn.execute("""DROP TABLE clients;""")

        conn.execute("""CREATE TABLE IF NOT EXISTS clients(
                 ID         TEXT PRIMARY KEY    NOT NULL,
                 name       TEXT                NOT NULL,
                 public_key TEXT                NOT NULL,
                 last_seen  TEXT,
                 aes        BLOB
                 );""")
        print("Clients table created if not exists successfully")

        conn.execute("""CREATE TABLE IF NOT EXISTS files(
                ID        TEXT     NOT NULL,
                file_name TEXT                NOT NULL,
                path_name TEXT     PRIMARY KEY           NOT NULL,
                verified  BOOLEAN
                );""")
        print("Files table created if not exists successfully")

        try:
            conn.execute("INSERT INTO clients (ID, name, public_key, aes) \
                  VALUES (1, 'Admin', 'key', 'aeskey')");
            conn.commit()
            print("Record Admin created successfully")
        except:
            print("admin is in DB")

        self._close(conn)

    def get_client_by_name(self, name):
        conn = self._connect()
        cursor = conn.execute(f"SELECT * from clients WHERE clients.name = '{name}'")
        print("select Client By Name done successfully")
        client_att = list()
        for row in cursor:
            for att in row:
                print(f"-  {att}")
                client_att.append(att)
        if client_att:
            existing_client = client.Client(*client_att)
            print(existing_client.__str__())
            self._close(conn)
            return existing_client
        else:
            self._close(conn)
            return None

    def get_client_by_id(self, id):
        conn = self._connect()
        cursor = conn.execute(f"SELECT * from clients WHERE clients.id = '{id}'")
        client_att = list()
        for row in cursor:
            for att in row:
                print(f"- = {att}")
                client_att.append(att)
        if client_att:
            existing_client = client.Client(*client_att)
            print(existing_client.__str__())
            self._close(conn)
            return existing_client
        else:
            self._close(conn)
            return None

    def get_file_by_file_name(self, file_name):
        conn = self._connect()
        cursor = conn.execute(f"SELECT * from files WHERE files.file_name = '{file_name}'")
        print("select file by file name done successfully")
        file_att = list()
        for row in cursor:
            for att in row:
                print(f"-  {att}")
                file_att.append(att)
        if file_att:
            existing_file = client.File(*file_att)
            self._close(conn)
            return existing_file
        else:
            self._close(conn)
            return None

    # aes = '{aes_key}'
    def update_client(self, client_name, public_key, aes_key):
        last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self._connect()
        aes_key1 = list(aes_key)
        cursor = conn.execute(f"UPDATE clients SET public_key = '{public_key}' , last_seen='{last_seen}' WHERE clients.name = '{client_name}'")
        cursor = conn.execute(f"UPDATE clients SET aes = '{aes_key1}' WHERE clients.name = '{client_name}'")
        conn.commit()
        self._close(conn)
        print("client keys updated successfully")

    def update_file_valid_crc(self, file_name):
        verified = True
        conn = self._connect()
        cursor = conn.execute(f"UPDATE files SET verified = '{verified}' WHERE files.file_name = '{file_name}'", )
        conn.commit()
        self._close(conn)
        print("file verified updated successfully")

    def add_new_client(self, name, public_key, aes_key):
        # id = uuid.uuid4().__str__()
        id = shortuuid.ShortUUID().random(length=16)
        last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self._connect()
        conn.execute(f"INSERT INTO clients (ID, name, public_key, last_seen, aes) \
              VALUES ('{id}', '{name}', '{public_key}', '{last_seen}', '{aes_key}')")
        conn.commit()
        self._close(conn)
        return id

    def add_new_file(self, id, file_name, path_name):
        verified = False
        conn = self._connect()
        conn.execute(f"INSERT INTO files (ID, file_name, path_name, verified) \
              VALUES ('{id}', '{file_name}', '{path_name}', '{verified}')")
        conn.commit()
        self._close(conn)


dao_service = _Dao()

