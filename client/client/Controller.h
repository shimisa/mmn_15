#pragma once
#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include "Client.h"
#include "Base64Wrapper.h"
#include "RSAWrapper.h"
#include "AESWrapper.h"
#include <locale>
#include <codecvt>
#include <boost/crc.hpp>      // for boost::crc_basic, boost::crc_optimal
#include <boost/cstdint.hpp>  // for boost::uint16_t
#include <algorithm>  // for std::for_each
#include <cstddef>    // for std::size_t
#include <iostream>   // for std::cout
#include <bitset>
#include <iostream>
#include "../zlib-1.2.13/zlib.h"





class Controller
{
private:
	Client* client;

	const std::string VERSION;
	std::string client_id;
	std::string code;
	std::string client_name;
	std::string payload;
	std::string payload_size;
	std::string crc;
	int re_try;
	string encrypted_file_content;

	std::string ME_INFO_FILE = "me.info";
	std::string TRANSFER_INFO_FILE = "transfer.info";
	std::string PRIV_KEY_FILE = "priv.key";

	std::string REGISTRATION_REQUEST = "12";
	std::string PUBLIC_KEY_REQUEST = "13";
	std::string LOGIN_REQUEST = "14";
	std::string FILE_REQUEST = "15";
	std::string VALID_CRC_REQUEST = "16";
	std::string BAD_CRC_REQUEST = "17";
	std::string FOUR_TIME_BAD_CRC_REQUEST = "18";
	//std::string REGISTRATION_SUCCESS = "20";
	//std::string REGISTRATION_FAILED = "21";
	//std::string PUBLIC_KEY_RECEIVED = "22";
	//std::string FILE_RECEIVED = "23";
	//std::string MSG_RECEIVED = "24";
	//std::string LOGIN_ACCEPT = "25";
	//std::string LOGIN_REJECT = "26";
	//std::string GENERAL_ERROR = "27";

	static const int REGISTRATION_SUCCESS = 20;
	static const int REGISTRATION_FAILED = 21;
	static const int PUBLIC_KEY_RECEIVED = 22;
	static const int FILE_RECEIVED = 23;
	static const int MSG_RECEIVED = 24;
	static const int LOGIN_ACCEPT = 25;
	static const int LOGIN_REJECT = 26;
	static const int GENERAL_ERROR = 27;

	static const int CLIENT_NAME_SIZE = 255;
	static const int FILE_SIZE = 255;
	static const int FOUR_CHARS = 4;
	static const int MAX_RE_TRIES = 3;

	static const int CLIENT_ID_POS = 7;

public:
	Controller(Client*);
	~Controller();

	int register_client();
	int login_client();
	int start_sending_file_flow();
	

	void handle_response(std::string response);
	//std::string handle_registration_res(std::string response);

	string get_crc(string str);

private:
	int connect_client(std::string name, std::string code);
	std::string set_payload_size();
	std::string get_request();
	void send_request();

	void handle_registration_success(std::string response);
	void handle_registration_failed(std::string response);
	void handle_public_key_received(std::string response);
	void handle_file_received(std::string response);
	void handle_msg_received(std::string response);
	void handle_login_reject(std::string response);
	void handle_general_error(std::string response);
	std::string create_store_rsa_keys();
	int send_public_key(std::string public_key);
	int store_keys(std::string public_key, std::string private_key);
	string read_key_from_file();
	void create_me_file(string public_key);
	string get_file_size(string file_to_send);
	string padd_value(std::string vlue, int length);
	string get_file_name_to_send();
	string get_file_content(string file_name);
	void retry_send_file();


};

