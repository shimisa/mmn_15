
#include <iostream>
#include <iomanip>
#include "Client.h"
#include "Controller.h"






int main()
{
	Client* client = new Client();
	client->connect("127.0.0.1", 1234);
	Controller controller(client);
	controller.register_client();
	delete client;

	return 0;
}

