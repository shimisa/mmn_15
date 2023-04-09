#pragma once
#include <iostream>
#include <boost/asio.hpp>
#include <string>


using namespace boost::asio;
using boost::asio::ip::tcp;
using ip::tcp;
using std::string;
using std::cout;
using std::endl;

class Client
{

private:
    boost::asio::io_context io_service;
    tcp::socket socket;
    tcp::resolver resolver;
    boost::system::error_code error;
    // buffer for getting response from server
    boost::asio::streambuf receive_buffer;

    bool loged_in;


public:

    Client();
    ~Client();

    int connect(string ip, int port);
    int send(string client_res);
    string receive();
    void login();
    void set_loged_in(bool loged_in);
    bool get_loged_in();
    bool clear_buff();


};
    