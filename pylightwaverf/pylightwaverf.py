import socket

class LightWaveRF():

	SOCKET_TIMEOUT = 2.0
	RX_PORT        = 9761
	TX_PORT        = 9760

	def __init__(self):

		# Set up transmission socket (allow broadcasting)
		tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tx_sock.settimeout(self.SOCKET_TIMEOUT)
		self.tx_sock = tx_sock

		# Set up receive socket
		rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tx_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		rx_sock.settimeout(self.SOCKET_TIMEOUT)
		rx_sock.bind(('0.0.0.0', self.RX_PORT))
		self.rx_sock = rx_sock

		# Set the initial msg_id
		self.msg_id = 1

		# Set the initial WiFiLink IP Address
		self.wifilink_ip = None


	def locate_wifilink(self):
		msg_data = '@?v'
		data, ip = self.send(msg_data, broadcast=True)
		self.wifilink_ip = ip


	def control(self, room=None, device=None, state=None, msg1=None, msg2=None):
		room   = 'R%d' % room   if room   is not None else ''
		device = 'D%d' % device if device is not None else ''
		state  = 'F%s' % state  if state  is not None else ''

		command  =  ''.join(['!', room, device, state])
		msg_data = '|'.join(filter(None,[command, msg1, msg2]))
		self.send(msg_data)


	def send(self, msg_data, broadcast=False):
		data = self.get_next_msg_id() + msg_data
		if broadcast:
			ip = '255.255.255.255'
		else:
			ip = self.wifilink_ip
		self.tx_sock.sendto(data, (ip, self.TX_PORT))

		data, addr = self.rx_sock.recvfrom(1024)
		ip, port   = addr

		return (data, ip)


	def get_next_msg_id(self):
		# Ensure we always generate msg_ids from 001-999
		msg_id = self.msg_id + 1
		if msg_id % 1000 == 0:
			msg_id = 1
		self.msg_id = msg_id
		return '%03d' % msg_id
