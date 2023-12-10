import socket
import multiprocessing

def handle_request(client_socket):
    try:
        request_data = client_socket.recv(1024)
        request_header_lines = request_data.decode().split("\r\n")
        request_line = request_header_lines[0]
        print("Request Line: " + request_line)

        file_name = request_line.split(" ")[1].strip("/")

        try:
            with open(file_name, 'rb') as file:
                response_content = file.read()
            response_header = "HTTP/1.1 200 OK\r\n"
        except FileNotFoundError:
            response_header = "HTTP/1.1 404 Not Found\r\n"
            response_content = b"File not found"

        server_header = "Server: 192.168.43.192\r\n\r\n"
        response = response_header.encode() + server_header.encode() + response_content

        client_socket.sendall(response)
    except Exception as e:
        print("Error handling request:", e)
    finally:
        client_socket.close()

def start_server(server_address, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_address, server_port))
    server_socket.listen(5)

    try:
        while True:
            print("Waiting for connection...")
            client_socket, client_addr = server_socket.accept()
            print("Connection established from:", client_addr)
            process = multiprocessing.Process(target=handle_request, args=(client_socket,))
            process.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    except Exception as e:
        print("Error:", e)
    finally:
        server_socket.close()

if __name__ == '__main__':
    ip_address = "192.168.43.192"
    port = 8000
    start_server(ip_address, port)

