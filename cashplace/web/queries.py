from aiohttp import web
from tickets import TicketsFactory
from errors import InvalidWebInput


class Queries:
    def __init__(self, config):
        self.config = config
        self.factory = TicketsFactory(config)

    def register_routes(self, app):
        app.add_routes([web.get("/btc/new/{coin}", self.create_ticket)])

    async def create_ticket(self, request):
        coin = request.match_info.get("coin").lower()
        ticket = self.factory.create_ticket(coin)
        if ticket:
            return web.json_response({"id": ticket.id})
        else:
            raise InvalidWebInput(f"unknown coin name: {coin}, valid names: [btc]")
