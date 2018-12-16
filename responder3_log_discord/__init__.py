#!/usr/bin/env python
import asyncio
import discord
import traceback

from responder3.core.logging.logtask import LoggerExtensionTask
from responder3.core.logging.logger import Logger, r3exception
from responder3.core.commons import Connection
from responder3.core.logging.log_objects import ConnectionOpened, Credential

class HoneyBot(discord.Client):
	def __init__(self, log_queue, msg_queue, token, channel_id):
		discord.Client.__init__(self)
		self.logger = Logger('HoneyBot', logQ = log_queue)
		self.token = token
		self.msg_queue = msg_queue
		self.stop_event = asyncio.Event()
		self.channel_id = channel_id

	async def process_msg(self):
		try:
			while True:
				embed = await self.msg_queue.get()
				try:
					channel = self.get_channel(self.channel_id)
					await self.send_message(channel, embed=embed)

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
					#https://cog-creators.github.io/discord-embed-sandbox/
					embed = discord.Embed(color=0x00dcff)
					embed.add_field(name="Source IP", value=str(msg.client_addr), inline=True)
					embed.add_field(name="Reverse DNS", value=str(msg.client_rdns), inline=True)
					embed.add_field(name="Protocol", value=str(msg.module), inline=False)
					embed.add_field(name="Credz", value=str(msg.fullhash), inline=False)
					embed.add_field(name="Info", value=str(self.extra_info), inline=True)
					embed.set_footer(text="https://github.com/skelsec/responder3")
					await self.msg_queue.put(embed)

				if isinstance(msg, ConnectionOpened) and self.log_connections == True:
					embed = discord.Embed(color=0x00dcff)
					embed.add_field(name="Source IP", value=str(msg.connection.remote_ip), inline=True)
					embed.add_field(name="Reverse DNS", value=str(msg.connection.local_port), inline=True)
					embed.add_field(name="Info", value=str(self.extra_info), inline=True)
					embed.set_footer(text="https://github.com/skelsec/responder3")
					await self.msg_queue.put(embed)

			except Exception as e:
				await self.logger.exception()

	async def setup(self):
		pass


if __name__ == '__main__':
	msg_queue = asyncio.Queue()
	h = HoneyBot(msg_queue)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(h.hb_start())
