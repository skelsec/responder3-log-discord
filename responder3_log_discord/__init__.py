# Work with Python 3.6
import asyncio
import discord
from responder3.core.logtask import LoggerExtensionTask
from responder3.core.commons import Credential

class HoneyBot(discord.Client):
	def __init__(self, msg_queue, token, channel_name = 'general'):
		discord.Client.__init__(self)
		self.token = token
		self.msg_queue = msg_queue
		self.stop_event = asyncio.Event()
		self.channel_name = channel_name
	
	async def process_msg(self):
		try:
			while True:
				embed = await self.msg_queue.get()
				try:
					for server in self.servers: 
						# Spin through every server
						for channel in server.channels: 
							# Channels on the server
							if channel.name == self.channel_name:
								if channel.permissions_for(server.me).send_messages:
									try:
										await self.send_message(channel, embed=embed)
									except Exception as e:
										print(str(e))
										continue
				except Exception as e:
					print(str(e))
				
		except Exception as e:
			print(e)
	
		
	async def on_message(self, message):
		return
		# we do not want the bot to reply to itself
		if message.author == self.user:
			return
			
		if message.content.startswith('!hello'):
			msg = 'Hello {0.author.mention}'.format(message)
			await self.send_message(message.channel, msg)

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')
		
	async def hb_start(self):
		asyncio.ensure_future(self.process_msg())
		await self.start(self.token)
		
class discordHandler(LoggerExtensionTask):
	def init(self):
		self.msg_queue = asyncio.Queue()
		self.token = self.config['token']
		self.channel_name = self.config['channel']
		self.extra_info = None
		if 'extra_info' in self.config:
			self.extra_info = self.config['extra_info']
		self.discordbot = HoneyBot(self.msg_queue, self.token, self.channel_name)
		
	async def main(self):
		asyncio.ensure_future(self.discordbot.hb_start())
		while True:
			msg = await self.result_queue.get()
			try:
				if isinstance(msg, Credential):
					print('HA! crez!')
					print('[discordhandler] %s' % msg)
					#https://anidiots.guide/first-bot/using-embeds-in-messages
					
					embed = discord.Embed(title = "Credntials", description="Here comes the next contestant!", color=3447003)
					embed.set_author(name = "HoneyBot")
					embed.add_field(name="Source IP", value=str(msg.client_addr), inline=False)
					embed.add_field(name="Reverse DNS", value=str(msg.client_rdns), inline=False)
					embed.add_field(name="Protocol", value= str(msg.module), inline=False)
					embed.add_field(name="Credz", value=str(msg.fullhash), inline=False)
					embed.add_field(name="Extra info", value=str(self.extra_info), inline=False)
					embed.set_footer(text= "© @SkelSec") #icon_url: client.user.avatarURL,
					await self.msg_queue.put(embed)
			except Exception as e:
				print(e)

				
			
	async def setup(self):
		pass


if __name__ == '__main__':
	msg_queue = asyncio.Queue()
	h= HoneyBot(msg_queue)
	
	loop = asyncio.get_event_loop()	
	loop.run_until_complete(h.hb_start())
	
	