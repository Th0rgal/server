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
                # configuration
                web.post("/ticket/{id}/setamount", self.set_ticket_amount),
                web.post("/ticket/{id}/setleftover", self.set_ticket_leftover),
                web.post("/ticket/{id}/setreceiver", self.set_ticket_receiver),
                # reception
                web.post("/ticket/{id}/askpayment", self.ask_payment),
                # received
                web.get("/ticket/{id}/balance", self.get_balance),
                # sending
                web.post("/ticket/{id}/confirm", self.confirm_reception),
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

    def get_infos(self, ticket, spender):
        response = {
            "status": ticket.status.value,
            "master": not spender ^ ticket.master_is_spender,
            "amount": ticket.amount,
        }
        if not ticket.leftover_address is None:
            response["leftover"] = ticket.leftover_address
        if not ticket.receiver_address is None:
            response["receiver"] = ticket.receiver_address
        return response

    async def get_ticket_infos(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized(
                "Wrong password"
            )  # so it's not possible to know if the ticket exists
        ticket = self.tickets_manager.tickets[ticket_id]
        query = request.query
        if not "spender" in query:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = query["spender"] == "true"
        ticket.verify_password(request.password, spender)
        return web.json_response(self.get_infos(ticket, spender))

    async def set_ticket_amount(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        if not "amount" in data:
            raise InvalidWebInput("you need to specify the amount parameter")
        if not "spender" in data:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = data["spender"] == "true"
        ticket.verify_password(request.password, spender)
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        if spender ^ ticket.master_is_spender:
            raise InvalidWebInput(
                "you need to be the master of this ticket to set its amount"
            )
        amount = int(float(data["amount"]))
        if amount == 0:
            raise InvalidWebInput("you need to specify an amount")
        minimal_amount = ticket.fetch_minimal_amount()
        if minimal_amount > amount:
            raise InvalidWebInput(f"minimal amount: {minimal_amount}")
        ticket.set_amount(amount)
        return web.json_response(self.get_infos(ticket, spender))

    async def set_ticket_leftover(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        spender = data["spender"] == "true" if "spender" in data else False
        if not spender:
            raise InvalidWebInput("you need to be the spender to set leftover address")
        if not "address" in data:
            raise InvalidWebInput("you need to specify the address parameter")

        ticket.verify_password(request.password, True)
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        ticket.set_leftover_address(data["address"])
        return web.json_response(self.get_infos(ticket, spender))

    async def set_ticket_receiver(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        spender = data["spender"] == "true" if "spender" in data else True
        if spender:
            raise InvalidWebInput("you need to be the receiver to set receiver address")
        if not "address" in data:
            raise InvalidWebInput("you need to specify the address parameter")

        ticket.verify_password(request.password, False)
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        ticket.set_receiver_address(data["address"])
        return web.json_response(self.get_infos(ticket, spender))

    async def ask_payment(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        if not "spender" in data:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = data["spender"] == "true"
        ticket.verify_password(request.password, spender)
        if ticket.status != TicketStatus.CONFIGURATION:
            raise InvalidWebInput(f"ticket is no longer in CONFIGURATION status")
        if ticket.leftover_address is None:
            raise Unauthorized(
                f"a leftover address has not been specified by the btc spender"
            )
        if ticket.receiver_address is None:
            raise Unauthorized(
                f"an output address has not been specified by the btc receiver"
            )
        ticket.set_status(TicketStatus.RECEPTION)
        return web.json_response(self.get_infos(ticket, spender))

    async def get_balance(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        query = request.query
        if not "spender" in query:
            raise InvalidWebInput("you need to specify the spender parameter")
        spender = query["spender"] == "true"
        ticket.verify_password(request.password, spender)
        ticket.refresh_balance()
        return web.json_response({"coin": ticket.coin, "balance": ticket.balance})

    async def confirm_reception(self, request):
        ticket_id = request.match_info.get("id")
        if ticket_id not in self.tickets_manager.tickets:
            raise Unauthorized("Wrong password")
        ticket = self.tickets_manager.tickets[ticket_id]
        data = await request.post()
        spender = data["spender"] == "true" if "spender" in data else False
        if not spender:
            raise InvalidWebInput("you need to be the spender to confirm the reception")
        if not "fast" in data:
            raise InvalidWebInput("you need to specify the fast parameter")
        fast = data["fast"] == "true"
        ticket.verify_password(request.password, True)
        if ticket.status != TicketStatus.RECEIVED:
            raise InvalidWebInput(f"ticket is no longer in RECEIVED status")
        ticket.finalize(fast)
        return web.json_response(self.get_infos(ticket, spender))
