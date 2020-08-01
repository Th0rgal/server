from aiohttp import web
from tickets import TicketsManager
from errors import InvalidWebInput


class Queries:
    def __init__(self, config):
        self.config = config
        self.tickets_manager = TicketsManager(config)
        self.tickets_manager.load()

    def register_routes(self, app):
        app.add_routes([web.get("/new/{coin}", self.create_ticket)])

    async def create_ticket(self, request):
        coin = request.match_info.get("coin").lower()
        ticket = self.tickets_manager.create_ticket(coin)
        if ticket:
            return web.json_response({"id": ticket.id})
        else:
            raise InvalidWebInput(f"unknown coin name: {coin}, valid names: [btc]")
