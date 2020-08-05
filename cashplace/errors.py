class UserError(Exception):
    pass


class InvalidWebInput(UserError):
    pass


class Unauthorized(UserError):
    pass


class TicketNotFound(Exception):
    pass
