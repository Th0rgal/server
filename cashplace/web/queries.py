from aiohttp import web
from tickets import TicketStatus
from errors import InvalidWebInput, Unauthorized
import time


class Queries:
    def __init__(self, config, tickets_manager):
        self.config = config
        self.tickets_manager = tickets_manager
        self.last_ticket_date = 0

    def register_routes(self, app):
        app.add_routes(
            [
                web.get("/new/{coin}", self.create_ticket),
                web.get("/ticket/{id}/infos", self.get_ticket_infos),
                web.post("/ticket/{id}/setup", self.setup_ticket),
                web.post("/ticket/{id}/askpayment", self.ask_payment),
                web.get("/ticket/{id}/balance", self.get_balance),
            ]
        )

    async def create_ticket(self, request):
        delay = time.time() - self.last_ticket_date
        if delay < self.config.global_delay:
            to_wait = self.config.global_delay - delay
            raise Unauthorized(f"wait {to_wait} more seconds to create a ticket")
        coin = request.match_info.get("coin").lower()
        ticket = self.tickets_manager.create_ticket(coin)
        if not ticket:
            raise InvalidWebInput(f"unknown coin name: {coin}, valid names: [btc]")
        self.last_ticket_date = time.time()
        return web.json_response({"id": ticket.id})

    async def get_ticket_infos(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise InvalidWebInput(f"unknown ticket id: {ticket_id}")
        ticket = self.tickets_manager.tickets[ticket_id]
        query = request.query
        if not "spender" in query:
            raise InvalidWebInput("you need to specify the spender parameter")
        ticket.verify_password(request.password, query["spender"] == "true")
        return web.json_response({"status": ticket.status.value})

    async def setup_ticket(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise InvalidWebInput(f"unknown ticket id: {ticket_id}")
        ticket = self.tickets_manager.tickets[ticket_id]
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        data = await request.post()
        if not "amount" in data:
            raise InvalidWebInput("you need to specify the amount parameter")
        if not "spender" in data:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = data["spender"] == "true"
        ticket.verify_password(request.password, spender)
        if spender ^ ticket.master_is_spender:
            raise InvalidWebInput(
                "you need to be the master of this ticket to set it up"
            )
        ticket.amount = data["amount"]
        ticket.update()
        return web.json_response({})

    async def ask_payment(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise InvalidWebInput(f"unknown ticket id: {ticket_id}")
        ticket = self.tickets_manager.tickets[ticket_id]
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        data = await request.post()
        if not "spender" in data:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = data["spender"] == "true"
        ticket.verify_password(request.password, spender)
        ticket.status = TicketStatus.PAYMENT
        ticket.update()
        return web.json_response({"status": ticket.status.value})

    async def get_balance(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise InvalidWebInput(f"unknown ticket id: {ticket_id}")
        ticket = self.tickets_manager.tickets[ticket_id]
        if ticket.status != TicketStatus.PAYMENT:
            raise InvalidWebInput(f"ticket is not in PAYMENT status")
        query = request.query
        if not "spender" in query:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = query["spender"] == "true"
        ticket.verify_password(request.password, spender)
        ticket.refresh_balance()
        return web.json_response({"coin": ticket.coin, "balance": ticket.balance})
