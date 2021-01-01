from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.conf import settings 

User = settings.AUTH_USER_MODEL

MSG_TYPE_MESSAGE = 0 # for standard messages

class PublicChatConsumer(AsyncJsonWebsocketConsumer):
	
	async def connect(self):
		"""
		called when the websocket is handshaking as part of 
		initial connection
		"""
		print("PublicChatConsumer: connect: " + str(self.scope['user']))
		await self.accept()
		
		# Add people to the group so they can get room messages
		await self.channel_layer.group_add(
			'public_chatroom_1',
			self.channel_name
			)

	async def disconnect(self, code):
		"""
		called when the websocket closes for any reason
		"""
		print("PublicChatConsumer: disconnect: " + str(self.scope['user']))
		pass

	async def receive_json(self, content):
		"""
		called when we get a text frame. channels will JSON-decode 
		the payload for us and pass it as the first argument
		"""
		command = content.get("command", None)
		print("PublicChatConsumer: receive_json: " + str(command))
		try:
			if command == "send":
				if len(content['message'].lstrip()) == 0:
					raise ClientError(422, "Sorry you can't send an empty message")
				await self.send_message(content['message'])
		except ClientError as e:
			errorData = {}
			errorData['error'] = e.code
			if e.message:
				errorData['message'] = e.message
			await self.send_json(errorData)

	async def send_message(self, message):
		await self.channel_layer.group_send(
			"public_chatroom_1",
			{
				"type": "chat.message",
				"profile_image": self.scope['user'].profile_image.url,
				"username": self.scope['user'].username,
				"user_id": self.scope['user'].id,
				"message": message,
			}
		)
	async def chat_message(self, event):
		"""
		called when someone has messaged our chat 
		"""
		# send a message down to the client
		print("PublicChatConsumer: chat_message from user #: " + str(event['user_id']))
		await self.send_json({
			"msg_type": MSG_TYPE_MESSAGE,
			"profile_image": event['profile_image'],
			"username": event['username'],
			"user_id": event['user_id'],
			"message": event['message'],
			})

# handling user errors 
class ClientError(Exception):
	"""
	Custom exception class that is caught by the websocket receive() 
	handler and translated into a send back to the client
	"""
	def __init__(self, code, message):
		super().__init__(code)
		self.code = code
		if message:
			self.message = message