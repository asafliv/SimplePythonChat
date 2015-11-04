# __author__ = 'asafliv'
#
import argparse, sys, socket, select, datetime


# Typing --help gives an explanation of the arguments
def clientArgsParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="The port the client wants to connect to", type=int)
    parser.add_argument("userName", help="The username of the client")
    parser.add_argument("hostName", help="The hostname the client wants to connect to")
    return parser.parse_args()


# Configure the client according to the given arguments
def client_config():
    global args, client_socket_created
    args = clientArgsParser();
    try:
        client_socket_created = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket_created.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()
    print 'Socket Created'
    host = args.hostName
    port = args.port
    try:
        remote_ip = socket.gethostbyname(host)

    except socket.gaierror:
        # could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()


    # set time-out for socket
    client_socket_created.settimeout(5);

    # Connect to remote server
    try:
        client_socket_created.connect((remote_ip, port))
    except:
        print '  timed out - Couldnt connect to server'
        # TODO enter option to retry
        client_socket_created.close()
        sys.exit()


client_config()


clientStillConnected = False
sendUserNameToServer = True
while not clientStillConnected:
    try:
        sys.stdout.flush()
        # Wait for input from stdin & socket
        inputready, outputready, exceptrdy = select.select([0, client_socket_created], [], [], 600)

        # TODO handle ecseption
        if not (inputready or exceptrdy):
            print '  timed out - After 1 minute client shuts down'
            print '  timed out - Closing session for: ' + args.userName + ', Come Again soon!!'
            client_socket_created.close()
            clientStillConnected = True
            break

        for i in inputready:
            if i == 0:
                data = sys.stdin.readline().strip()
                if data:
                    if data=='--userList':
                        client_socket_created.sendall(data)
                        continue
                    client_socket_created.sendall(str(args.userName) + ": " + data)
            elif i == client_socket_created:
                try:
                    data = client_socket_created.recv(1024)
                    if not data:
                        print 'Server is down - Please come back later'
                        clientStillConnected = True
                        break
                    else:
                        # We need to update the server with the client username
                        if sendUserNameToServer:
                            client_socket_created.sendall("userName/"+str(args.userName))
                            sendUserNameToServer = False;

                        # Server Declined our connection because of a duplication of the username
                        if data == "DUPNAME":
                            sys.stdout.write('\n' +time+": " + args.userName +
                                             ' Already exists - Please connect with a new username\n')
                            client_socket_created.close()
                            clientStillConnected = True
                            continue

                        from datetime import datetime
                        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S');
                        sys.stdout.write('\n' +time+": " + data + '\n')
                        # make a sound
                        print('\a'),
                        sys.stdout.flush()
                except socket.error, e:
                    if e.errno == 54:
                        print >> sys.stderr, "Max connection to server"
                    else:
                        print >> sys.stderr, "Error connecting to server"
                    client_socket_created.close()
                    clientStillConnected = True
                    break

    except KeyboardInterrupt:
        print '\nClient Interrupted.'
        client_socket_created.sendall("CLOSEDCONNECTION")
        client_socket_created.close()
        clientStillConnected = True
        break
