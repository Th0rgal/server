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
        app.add_routes([web.post("/login/{id}", self.login_to_ticket)])

    async def create_ticket(self, request):
        coin = request.match_info.get("coin").lower()
        ticket = self.tickets_manager.create_ticket(coin)
        if not ticket:
            raise InvalidWebInput(f"unknown coin name: {coin}, valid names: [btc]")
        return web.json_response({"id": ticket.id})

    async def login_to_ticket(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise InvalidWebInput(f"unknown ticket id: {ticket_id}")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        if not "spender" in data:
            raise InvalidWebInput("You need to specify the spender parameter")
        ticket.verify_password(request.password, data["spender"])
        return web.json_response({"status": ticket.status.value})
