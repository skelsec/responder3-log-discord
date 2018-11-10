# Work with Python 3.6
import asyncio
import discord
import traceback

from responder3.core.logtask import LoggerExtensionTask, Logger, r3exception
from responder3.core.commons import Credential, ConnectionOpened

class HoneyBot(discord.Client):
	def __init__(self, log_queue, msg_queue, token, channel_name = 'general'):
		discord.Client.__init__(self)
		self.logger = Logger('HoneyBot', logQ = log_queue)
		self.token = token
		self.msg_queue = msg_queue
		self.stop_event = asyncio.Event()
		self.channel_name = channel_name
	
	async def process_msg(self):
		try:
			while True:
				embed = await self.msg_queue.get()
				try:
					for channel in self.get_all_channels(): 
						if channel.name == self.channel_name:
							try:
								await self.send_message(channel, embed=embed)
							except Exception as e:
								await self.logger.exception()
								continue
				except Exception as e:
					await self.logger.exception()
				
		except Exception as e:
			await self.logger.exception()
	
		
	async def on_message(self, message):
		return

	async def on_error(self, event, *args, **kwargs):
		await self.logger.exception('Event raised an exception! Event name: %s' % str(event))

	async def on_ready(self):
		await self.logger.info('Logged on to Discord! Username: %s UserID: %s' % (self.user.name, self.user.id))
		
	async def hb_start(self):
		asyncio.ensure_future(self.process_msg())
		await self.start(self.token)
		
class discordHandler(LoggerExtensionTask):
	def init(self):
		try:
			self.msg_queue = asyncio.Queue()
			self.token = self.config['token']
			self.channel_name = self.config['channel']
			self.extra_info = None
			self.log_connections = False
			if 'extra_info' in self.config:
				self.extra_info = self.config['extra_info']
			if 'log_connections' in self.config and self.config['log_connections'] == True:
				self.log_connections = True
			self.discordbot = HoneyBot(self.log_queue, self.msg_queue, self.token, self.channel_name)
		except Exception as e:
			traceback.print_exc()

	async def main(self):
		asyncio.ensure_future(self.discordbot.hb_start())
		while True:
			msg = await self.result_queue.get()
			try:
				if isinstance(msg, Credential):
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

				if isinstance(msg, ConnectionOpened) and self.log_connections == True:
					embed = discord.Embed(title = "Connection", description="We have a visitor", color=3447003)
					embed.set_author(name = "HoneyBot")
					embed.add_field(name="Source IP", value=str(msg.connection.remote_ip), inline=False)
					embed.add_field(name="Dst port", value= str(msg.connection.local_port), inline=False)
					embed.add_field(name="Reverse DNS", value=str(msg.connection.remote_dns), inline=False)
					embed.add_field(name="Extra info", value=str(self.extra_info), inline=False)
					embed.set_footer(text= "© @SkelSec") #icon_url: client.user.avatarURL,
					await self.msg_queue.put(embed)

			except Exception as e:
				await self.logger.exception()

	async def setup(self):
		pass


if __name__ == '__main__':
	msg_queue = asyncio.Queue()
	h= HoneyBot(msg_queue)
	
	loop = asyncio.get_event_loop()	
	loop.run_until_complete(h.hb_start())
	
	
