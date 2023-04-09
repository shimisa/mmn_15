
#include "Client.h"




Client::Client() :
	socket(io_service), resolver(io_service), loged_in(false)

{
	
}

Client::~Client()
{
	const string disconnect = "!DISCONNECT";
	send(disconnect);
	socket.close();
}

int Client::connect(string ip, int port)
{
	char address[] = "127.0.0.1";
	char port1[] = "1234";
	boost::asio::connect(socket, resolver.resolve(address, port1));
	//socket.connect(tcp::endpoint(boost::asio::ip::address::from_string(ip), port));
	return 0;
}


int Client::send(string client_res)
{
	const int max_length = 1042;
	char request[max_length];
	boost::asio::write(socket, boost::asio::buffer(client_res), error);
	if (!error) {
		cout << "\nClient sent: " << client_res << endl;
	}
	else {
		cout << "send failed: " << error.message() << endl;
	}

	return 0;
}

string Client::receive()
{
	string server_res;
	boost::asio::read_until(socket, receive_buffer, "");
	const char* data;
	if (error && error != boost::asio::error::eof) {
		cout << "receive failed: " << error.message() << endl;
	}
	else {
		auto size = receive_buffer.size();
		const char* data = boost::asio::buffer_cast<const char*>(receive_buffer.data());
		server_res = string(data);
		receive_buffer.consume(size);
		cout << "\nClient received: " << server_res << endl;
	}
	return server_res; 
}



void Client::login()
{

}

void Client::set_loged_in(bool loged_in)
{
	this->loged_in = loged_in;
}

bool Client::get_loged_in()
{
	return this->loged_in;
}

bool Client::clear_buff()
{
	return true;
}
