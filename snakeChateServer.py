# __author__ = 'asafliv'


# Socket server in python using select function
# TODO handle server arguments
# TODO max size of the messege?
import socket, select, sys, argparse

CONNECTION_LIST = []  # list of sockets including server socket
client_List = []  # list of connections connected to the server
user_dic = {}  # Dictionary of user data build as (socket_peer_name (key) : userName (value))


# Typing --help gives an explanation of the arguments
def server_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="The port the client wants to connect to", type=int)
    parser.add_argument("hostName", help="The username of the client")
    return parser.parse_args()


def config_server():
    server_setup_args = server_args_parser()
    server_socket_created = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_created.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket_created.bind((server_setup_args.hostName, server_setup_args.port))
    except socket.error, msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    server_socket_created.listen(5)
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket_created)

    print 'Snake chat server is alive and ready to get to work'
    print 'Today we are working on ' + str(server_socket_created.getsockname()) + ' so come on up and chat!!'

    return server_socket_created


def update_user_list(user_sock, user_name_to_update):
    user_dic[user_sock] = user_name_to_update


# Function to handle Server removement of Client:
def remove_client(socket_to_remove):
    print("Client " + str(socket_to_remove.getpeername()) + " is offline")
    # Check if the user is In the user dictionary and remove it
    if socket_to_remove.getpeername() in user_dic:
        del (user_dic[socket_to_remove.getpeername()])
    # Slose socket
    socket_to_remove.close()
    # Remove from the lists of sockets to listen to
    CONNECTION_LIST.remove(socket_to_remove)
    client_List.remove(socket_to_remove)


# Parses the data sent from the Client according to the set protocol
def parse_sent_data(data, socket):
    if data[0:9] == 'userName/':
        # Username the client chose for himself
        user_connected = data[9:len(data)]
        dup = False
        # Check if it is a duplicate
        for key, val in user_dic:
            if user_dic[key, val] == user_connected:
                dup = True;
                break
        if (dup):
            socket.sendall(str("DUPNAME"))
            return None
        # Add to the client dicionary the userName as value and the sockname as key
        update_user_list(socket.getpeername(), user_connected)
        return None
    elif data[0:10] == '--userList':
        # User requested the user list of the site
        user_names_to_return = [];
        for (sock_String, port_value) in user_dic:
            user_names_to_return.append(user_dic[(sock_String, port_value)])
        socket.sendall(str(user_names_to_return))
        return None

    elif data == "CLOSEDCONNECTION":
        # Client has signaled it is disconnecting
        remove_client(socket)
        return None
    else:
        return data


config_server()

while 1:
    # Get the list sockets which are ready to be read through select
    # todo select timeout
    timeOut = 600
    try:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], CONNECTION_LIST, timeOut)
        for socket in read_sockets:

            # New connection
            if socket == CONNECTION_LIST[0]:
                # New client wants to join the chat
                if len(client_List) > 10:
                    # Already 10 clients are connected
                    print >> sys.stderr, 'Client MAX number reached'
                    CONNECTION_LIST.remove(socket)
                    socket.close()
                    continue
                try:
                    # Accept should work
                    sockfd, addr = CONNECTION_LIST[0].accept()
                except socket.error:
                    print >> sys.stderr, 'Error accepting a socket'
                    continue

                # NEW CLIENT CONNECTION!!!
                CONNECTION_LIST.append(sockfd)
                # Add a unique attribute to the client list for
                client_List.append(sockfd)
                sockfd.sendall("WELCOME TO SNAKECHAT, PLEASE BEHAVE :) ......");
                print "Client (%s, %s) connected" % addr
                continue

            else:
                # Data from client, process it
                try:
                    data = socket.recv(1024)
                    if data:
                        # Parse the recieved data
                        server_reply = parse_sent_data(data, socket)
                        if server_reply is None:
                            continue
                        else:
                            # Broadcast the messege to all clientes
                            for sender in client_List:
                                if sender != socket:
                                    try:
                                        sender.sendall(data);
                                    except socket.error, e:
                                        print(sender + "Error sending this client data")
                                        continue
                        continue;
                    else:
                        print("Client (%s, %s) is offline" % socket.getpeername())
                        remove_client(socket)
                        continue
                # client disconnected, so remove from socket list
                except Exception, errorcode:
                    print(socket, "Client (%s) is offline" % socket)
                    remove_client(socket)
                    continue
                    # If one of the client sockets got an error
        for errorSocket in error_sockets:
            print >> sys.stderr, 'Got an error from this Socket:', errorSocket.getpeername()
            # Stop listening for input on the connection
            remove_client(socket)
            continue
        if not (read_sockets or error_sockets):
            print '  timed out - No connections were recorded for 10 minutes'
            print '  timed out - Closing server'
            CONNECTION_LIST[0].close()
            break
    except KeyboardInterrupt:
        print 'Interrupted.'
        CONNECTION_LIST[0].close()
        break

CONNECTION_LIST[0].close()
