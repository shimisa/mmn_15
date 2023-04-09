#include "Controller.h"


void Controller::handle_response(std::string response)
{
	int res_code = stoi(response.substr(1, 2));

	switch (res_code) {
	case REGISTRATION_SUCCESS:
		handle_registration_success(response);
		break;
	case REGISTRATION_FAILED:
		handle_registration_failed(response);
		break;
	case PUBLIC_KEY_RECEIVED:
		handle_public_key_received(response);
		break;
	case FILE_RECEIVED:
		handle_file_received(response);
		break;
	case MSG_RECEIVED:
		handle_msg_received(response);
		break;
	case LOGIN_ACCEPT:
		handle_public_key_received(response);
		break;
	case LOGIN_REJECT:
		handle_login_reject(response);
		break;
	case GENERAL_ERROR:
		handle_general_error(response);
		break;

	}
	client->clear_buff();
}

void Controller::send_request()
{
	set_payload_size();
	std::string request = get_request();
	client->send(request);
	std::string response = client->receive();
	handle_response(response);
}

void Controller::handle_general_error(std::string response)
{
	std::cout << "SERVER: GENERAL_ERROR";
}

void Controller::handle_login_reject(std::string server_res)
{
	std::cout << "SERVER: LOGIN_REJECT";
	code = REGISTRATION_REQUEST;
	std::ifstream transfer_info_file(TRANSFER_INFO_FILE);
	// Get and drop a line
	transfer_info_file.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
	string name;
	std::getline(transfer_info_file, name);
	connect_client(name, code);
}

void Controller::handle_msg_received(std::string response)
{
	std::cout << "SERVER: MSG_RECEIVED";
}

void Controller::handle_registration_success(std::string server_res)
{
	std::cout << "SERVER: REGISTRATION_SUCCESS";
	client_id = server_res.substr(CLIENT_ID_POS);
	client->set_loged_in(true);
	std::string public_key = create_store_rsa_keys();
	create_me_file(public_key);
	send_public_key(public_key);
}

void Controller::handle_registration_failed(std::string server_res)
{
	std::cout << "SERVER: REGISTRATION_FAILED";
}

void Controller::handle_public_key_received(std::string server_res)
{
	std::cout << "SERVER: PUBLIC_KEY_RECEIVED";
	string clientId_plus_aes_key = server_res.substr(7);
	client_id = clientId_plus_aes_key.substr(0, 16);
	string encrypted_aes_key = clientId_plus_aes_key.substr(16);
	string base64_private_key = read_key_from_file();
	//encrypted_aes_key = encrypted_aes_key.substr(2, encrypted_aes_key.length() - 3);

	

	//std::string delimiter = "b";
	//std::string str = "";

	//size_t pos = 0;
	//std::string token;
	//while ((pos = encrypted_aes_key.find(delimiter)) != std::string::npos) {
	//	token = encrypted_aes_key.substr(0, pos);
	//	std::cout << token << std::endl;
	//	char c1 = static_cast<char>(std::stoi(token, nullptr, 2) + 64);
	//	str += c1;
	//	encrypted_aes_key.erase(0, pos + delimiter.length());
	//}

	
	//wchar_t uchars[] = { 0x5e9, 0x5dc, 0x5d5, 0x5dd, 0 };
	//std::wstring_convert<std::codecvt_utf8<wchar_t>> conv;
	//std::string s = conv.to_bytes(uchars);
	//std::wstring ws2 = conv.from_bytes(s);
	//std::cout << std::boolalpha
	//	<< (s == "\xd7\xa9\xd7\x9c\xd7\x95\xd7\x9d") << '\n'
	//	<< (ws2 == uchars) << '\n';
	//cout << uchars;
	//cout << s;

	std::string x = Base64Wrapper::encode(encrypted_aes_key);

	// create another RSA decryptor using an existing private key
	RSAPrivateWrapper rsapriv_other(Base64Wrapper::decode(base64_private_key));
	std::string decrypted_aes_key = rsapriv_other.decrypt(encrypted_aes_key);
	//std::string decrypted_aes_key = rsapriv_other.decrypt(encrypted_aes_key.c_str(), encrypted_aes_key.length());
	// Encrypt file with the AES key 
	

	// 1. Generate a key and initialize an AESWrapper. You can also create AESWrapper with default constructor which will automatically generates a random key.
	unsigned char* key = reinterpret_cast<unsigned char*>(&decrypted_aes_key[0]);
	AESWrapper aes(key, AESWrapper::DEFAULT_KEYLENGTH);

	string file_name = get_file_name_to_send();
	string file_content = get_file_content(file_name);

	// 2. encrypt a message (plain text)
	std::string encrypted_file_to_send = aes.encrypt(file_content.c_str(), file_content.length());
	encrypted_file_content = file_content;
	crc = get_crc(file_content);
	code = FILE_REQUEST;
	//payload = get_file_size(encrypted_file_to_send) + padd_value(file_name, FILE_SIZE) + encrypted_file_to_send;
	payload = get_file_size(encrypted_file_to_send) + padd_value(file_name, FILE_SIZE) + encrypted_file_to_send;
	send_request();

}

void Controller::handle_file_received(std::string server_res)
{
	std::cout << "SERVER: FILE_RECEIVED";
	string res_payload = server_res.substr(7);
	client_id = res_payload.substr(0, 16);
	res_payload = res_payload.substr(16);
	string content_size = res_payload.substr(0, 4);
	res_payload = res_payload.substr(4);
	string file_name = res_payload.substr(0, 255);
	res_payload = res_payload.substr(255);
	string cksum = res_payload.substr(0, 4);

	bool valid_crc = (cksum == crc);

	if (valid_crc)
	{
		code = VALID_CRC_REQUEST;
		payload = file_name;
		send_request();
	}
	else
	{
		code = BAD_CRC_REQUEST;
		payload = file_name;
		send_request();
		retry_send_file();
		
		
	}
}


std::string Controller::create_store_rsa_keys()
{
	// 1. Create an RSA decryptor. this is done here to generate a new private/public key pair
	RSAPrivateWrapper rsapriv;

	// 2. get the public key
	std::string pubkey = rsapriv.getPublicKey();
	std::string privkey = rsapriv.getPrivateKey();

	std::string base64_privkey = Base64Wrapper::encode(privkey);
	std::string base64_bupkey = Base64Wrapper::encode(pubkey);

	store_keys(base64_bupkey, base64_privkey);

	base64_bupkey = "-----BEGIN PUBLIC KEY-----\n" + base64_bupkey + "-----END PUBLIC KEY-----";

	return base64_bupkey;
}

int Controller::send_public_key(std::string public_key)
{
	code = PUBLIC_KEY_REQUEST;
	payload = client_name + public_key;
	send_request();
	return 0;
}

int Controller::store_keys(std::string pub_key, std::string priv_key)
{
	// Create and open a text file
	std::ofstream privkey_file(PRIV_KEY_FILE);
	privkey_file << priv_key;
	privkey_file.close();
	return 0;
}

string Controller::read_key_from_file()
{
	string private_key;
	string tmp_str;
	// Read from the text file
	std::ifstream privkey_file(PRIV_KEY_FILE);
	while (std::getline(privkey_file, tmp_str)) {
		// Output the text from the file
		private_key = private_key + tmp_str;
	}

	return private_key;
}

void Controller::create_me_file(string public_key)
{
	std::ofstream transfer_info_file(ME_INFO_FILE);
	transfer_info_file << client_name.substr(0, client_name.find("0")) + "\n";
	transfer_info_file << client_id + "\n";
	transfer_info_file << public_key + "\n";
	transfer_info_file.close();
}

Controller::Controller(Client* client):
	client_id("0000000000000000"), VERSION("2"), re_try(0)
{
	this->client = client;
}

Controller::~Controller()
{
}

int Controller::register_client()
{
	code = REGISTRATION_REQUEST;
	std::ifstream me_info_file(ME_INFO_FILE);
	if (me_info_file.good())
	{
		me_info_file.close();
		login_client();
		return 0;
	}
	std::ifstream transfer_info_file(TRANSFER_INFO_FILE);
	// Get and drop a line
	transfer_info_file.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
	string name;
	std::getline(transfer_info_file, name);
	connect_client(name, code);
	return 0;
}

int Controller::login_client()
{
	code = LOGIN_REQUEST;

	std::ifstream me_info_file(ME_INFO_FILE);
	string name;
	std::getline(me_info_file, name);
	connect_client(name, code);
	return 0;
}

int Controller::start_sending_file_flow()
{
	return 0;
}

int Controller::connect_client(std::string name, std::string code)
{
	std::string tmp = name;
	// padding with 0 ae suffix
	while (tmp.length() < CLIENT_NAME_SIZE)
	{
		tmp = tmp + "0";
	}
	client_name = tmp;
	payload = client_name;

	send_request();
	return 0;
}


std::string Controller::set_payload_size()
{
	payload_size = std::to_string(payload.length());
	while (payload_size.length() < FOUR_CHARS)
	{
		payload_size = "0" + payload_size;
	}
	return std::to_string(payload.length());
}

std::string Controller::get_file_size(std::string file_to_send)
{
	string res = std::to_string(file_to_send.length());
	while (res.length() < FOUR_CHARS)
	{
		res = "0" + res;
	}
	return res;
}

string Controller::get_crc(string str)
{
	const char* data = str.c_str();
	/*
	 * Calculates the CRC-32 checksum of the given data.
	 */
	unsigned long crc = crc32(0L, Z_NULL, 0);
	crc = crc32(crc, (const Bytef*)data, str.length());
	string crc_str = std::to_string(crc).substr(0, 4);
	return crc_str;

}

std::string Controller::padd_value(std::string vlue, int length)
{
	string res = vlue;
	while (res.length() < length)
	{
		res = res + "0";
	}
	return res;
}

string Controller::get_file_name_to_send()
{
	string file_name;
	std::ifstream transfer_info_file(TRANSFER_INFO_FILE);
	// Get and drop a line
	transfer_info_file.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
	transfer_info_file.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
	std::getline(transfer_info_file, file_name);
	transfer_info_file.close();
	return file_name;
}

string Controller::get_file_content(string file_name)
{
	std::ifstream file_to_send(file_name);
	if (!file_to_send.good())
	{
		file_to_send.close();
		throw EXCEPTION_ACCESS_VIOLATION;
		return std::string();
	}
	string file_content((std::istreambuf_iterator<char>(file_to_send)),
		(std::istreambuf_iterator<char>()));
	file_to_send.close();
	return file_content;
}

void Controller::retry_send_file()
{
	if (re_try >= MAX_RE_TRIES)
	{
		code = FOUR_TIME_BAD_CRC_REQUEST;
		string file_name = get_file_name_to_send();
		payload = padd_value(file_name, FILE_SIZE);
		send_request();

	}
	else
	{
		code = FILE_REQUEST;
		string file_name = get_file_name_to_send();
		crc = get_crc(encrypted_file_content);
		payload = get_file_size(encrypted_file_content) + padd_value(file_name, FILE_SIZE) + encrypted_file_content;
		re_try += 1;
		send_request();
	}
}

std::string Controller::get_request()
{
	return client_id + VERSION + code + payload_size + payload;
}
