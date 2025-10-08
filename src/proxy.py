import asyncio
import socket
import logging

logging.basicConfig(
    filename='logs/proxy.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
class Proxy():
    def __init__(self, user: str, password: str, ip: str, port: int):
        self.PROXY_USER = user
        self.PROXY_PASS = password    
        self.PROXY_IP = ip
        self.PROXY_PORT = port
        
    async def tunnel(self, reader, writer):
        """Encaminha dados entre duas conexões."""
        try:
            while True:
                data = await reader.read(2048)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except asyncio.CancelledError:
            pass
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()

    async def handle_client_hybrid(self, client_reader, client_writer):
        """Lida com a conexão de um novo cliente, detectando se é SOCKS5 ou HTTP."""
        addr = client_writer.get_extra_info('peername')
        logging.info(f"[*] Nova conexão de: {addr}")
        
        try:
            # CORREÇÃO: Lê o primeiro byte em vez de usar peek()
            first_byte = await client_reader.read(1)
            if not first_byte:
                logging.info(f"[*] Conexão de {addr} fechada antes de enviar dados.")
                return

            # Se o primeiro byte for 0x05, é SOCKS5
            if first_byte == b'\x05':
                # Passa o primeiro byte para o handler SOCKS5
                await self.handle_socks5(client_reader, client_writer, addr, first_byte)
            # Caso contrário, assume que é HTTP
            else:
                # Passa o primeiro byte para o handler HTTP
                await self.handle_http(client_reader, client_writer, addr, first_byte)

        except asyncio.IncompleteReadError:
            logging.info(f"[*] Conexão de {addr} fechada prematuramente.")
        except Exception as e:
            logging.info(f"!! Unhandled exception in hybrid handler for {addr}: {e}")
            if not client_writer.is_closing():
                client_writer.close()
                await client_writer.wait_closed()

    async def handle_http(self, client_reader, client_writer, addr, first_byte):
        """Trata a conexão como HTTP CONNECT, usando o primeiro byte já lido."""
        logging.info(f"[*] Tratando {addr} como conexão HTTP CONNECT.")
        dest_writer = None
        try:
            # CORREÇÃO: Combina o primeiro byte com o resto dos cabeçalhos
            remaining_headers = await client_reader.read(4095)
            headers_bytes = first_byte + remaining_headers
            headers_str = headers_bytes.decode('utf-8', errors='ignore')
            
            first_line = headers_str.split('\r\n')[0]
            if 'CONNECT' not in first_line:
                logging.info(f"[-] Requisição HTTP de {addr} não é um CONNECT. Negado.")
                client_writer.close()
                await client_writer.wait_closed()
                return

            target_host, target_port = first_line.split(' ')[1].split(':')
            
            dest_reader, dest_writer = await asyncio.open_connection(target_host, int(target_port))
            
            client_writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            await client_writer.drain()
            
            logging.info(f"[*] Túnel HTTP estabelecido para {addr} -> {target_host}:{target_port}")

            # Se houver dados "extras" após os cabeçalhos CONNECT, encaminhe-os primeiro
            # Isso pode acontecer se o cliente for rápido (pipelining)
            header_end_pos = headers_bytes.find(b'\r\n\r\n')
            if header_end_pos != -1:
                extra_data = headers_bytes[header_end_pos + 4:]
                if extra_data:
                    dest_writer.write(extra_data)
                    await dest_writer.drain()

            task1 = asyncio.create_task(self.tunnel(client_reader, dest_writer))
            task2 = asyncio.create_task(self.tunnel(dest_reader, client_writer))
            
            await asyncio.gather(task1, task2)

        except Exception as e:
            logging.info(f"[!] Erro ao lidar com o cliente HTTP {addr}: {e}")
        finally:
            if not client_writer.is_closing():
                client_writer.close()
                await client_writer.wait_closed()
            if dest_writer and not dest_writer.is_closing():
                dest_writer.close()
                await dest_writer.wait_closed()
            logging.info(f"[*] Conexão HTTP de {addr} fechada.")

    async def handle_socks5(self, client_reader, client_writer, addr, first_byte):
        """Trata a conexão como SOCKS5, usando o primeiro byte já lido."""
        logging.info(f"[*] Tratando {addr} como conexão SOCKS5.")
        dest_writer = None
        try:
            # CORREÇÃO: O primeiro byte (versão) já foi lido, então lemos apenas o próximo
            version = first_byte[0]
            nmethods_byte = await client_reader.readexactly(1)
            nmethods = nmethods_byte[0]

            if version != 5: return
            
            methods = await client_reader.readexactly(nmethods)
            if 2 not in methods: # Autenticação por User/Pass
                client_writer.write(b'\x05\xff')
                await client_writer.drain()
                return
                
            client_writer.write(b'\x05\x02')
            await client_writer.drain()
            
            # Continua com a lógica de autenticação e conexão SOCKS5...
            auth_header = await client_reader.readexactly(2)
            auth_ver, ulen = auth_header
            username = (await client_reader.readexactly(ulen)).decode('utf-8')
            plen = (await client_reader.readexactly(1))[0]
            password = (await client_reader.readexactly(plen)).decode('utf-8')
            if username == self.PROXY_USER and password == self.PROXY_PASS:
                logging.info(f"[+] Autenticação SOCKS5 bem-sucedida para {addr}")
                client_writer.write(b'\x01\x00')
                await client_writer.drain()
            else:
                logging.info(f"[-] Falha na autenticação SOCKS5 para {addr}")
                client_writer.write(b'\x01\x01')
                await client_writer.drain()
                return

            request_header = await client_reader.readexactly(4)
            version, cmd, rsv, atyp = request_header
            if version != 5 or cmd != 1: return
            
            if atyp == 3: # Domain
                domain_len = (await client_reader.readexactly(1))[0]
                target_host = (await client_reader.readexactly(domain_len)).decode('utf-8')
            elif atyp == 1: # IPv4
                ip_bytes = await client_reader.readexactly(4)
                target_host = socket.inet_ntoa(ip_bytes)
            else: # Ignora IPv6 e outros tipos
                logging.info(f"[-] Tipo de endereço SOCKS5 não suportado ({atyp}) de {addr}.")
                return

            target_port = int.from_bytes(await client_reader.readexactly(2), 'big')
            
            dest_reader, dest_writer = await asyncio.open_connection(target_host, target_port)
            logging.info(f"[*] Túnel SOCKS5 estabelecido para {addr} -> {target_host}:{target_port}")
            
            client_writer.write(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
            await client_writer.drain()
            
            task1 = asyncio.create_task(self.tunnel(client_reader, dest_writer))
            task2 = asyncio.create_task(self.tunnel(dest_reader, client_writer))
            await asyncio.gather(task1, task2)

        except Exception as e:
            logging.info(f"[!] Erro ao lidar com o cliente SOCKS5 {addr}: {e}")
        finally:
            if not client_writer.is_closing():
                client_writer.close()
                await client_writer.wait_closed()
            if dest_writer and not dest_writer.is_closing():
                dest_writer.close()
                await dest_writer.wait_closed()
            logging.info(f"[*] Conexão SOCKS5 de {addr} fechada.")

    async def __proxy(self):
        server = await asyncio.start_server(self.handle_client_hybrid, self.PROXY_IP, self.PROXY_PORT)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        logging.info(f'[*] Proxy HÍBRIDO (SOCKS5+HTTP) rodando em {addrs}')

        async with server:
            await server.serve_forever()

    def start_proxy(self):
        try:
            asyncio.run(self.__proxy())
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")