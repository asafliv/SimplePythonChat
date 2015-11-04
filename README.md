# SimplePythonChat

A very simple Python based server & client.
I've created 2 files:
snakeChatServer.py - The server script
snakeChatClient.py - The client script

Server design and implementation:
1. Start the server, in order to start it you will need to supply the right arguments:
python snakeChatServer <portToListen> <hostname>
(typing "--help" will show you the exact information you need)
2. The server supports up to 10! client instances.
3. Snake chat is a broadcast chat, what the client types is sent to all clients that are connectd.
4. The server uses the socket select command to listen to the clients that are connected to him.
5. If the server is closed his connected clients are closed immediately.
6. If no client is connected within 10 minutes time span then the server shuts down.

Client design and implementation:
1. in order to start it you will need to supply the right arguments:
python snakeChateServer <server_port_to_connect> <client_ userName> <server_hostname>
(typing "--help" will show you the exact information you need)
2. If you chose an already connected username you will be requested to connect again.
3. If a user types "--userList" he will receive all the users that are connected.

Thanks for using SnakeChat :)
