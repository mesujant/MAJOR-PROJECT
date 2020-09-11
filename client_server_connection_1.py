import socket as s
def run_server(target_host , port):
	#global server_count
	server_count = 1	
	server = s.socket()
	server.bind((target_host , port))
	server.listen(5)
	print(f"server no : {server_count} Running...")
	while True:
		client_socket , addr = server.accept()
		print(f"connect establised from {addr[0]} {addr[1]} @ {server_count}")
		client_socket.close()


def connect_to_server(target_host  , port):
	client = s.socket()
	client.connect((target_host,port))
