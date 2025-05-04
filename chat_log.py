import socket

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'TWITCH_CHANNEL'
token = 'TWITCH_TOKEN'  # from https://twitchapps.com/tmi/
channel = 'TWITCH_CHANNEL'

sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))

with open('all_chat.log', 'a', encoding='utf-8') as log_file:
    while True:
        resp = sock.recv(2048).decode('utf-8')
        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))
        else:
            print(resp)
            log_file.write(resp + '\n')
            log_file.flush()
