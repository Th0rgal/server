import aiohttp_cors
from aiohttp import web

class WebAPI:
    def __init__(self, config):
        self.config = config
        self.app = web.Application(
            middlewares=[self.error_middleware],
            client_max_size=0.5 * 2 ** 30,
        )  # 0.5 GiB
        self.app.add_routes(
            [
                #web.get("/debug", self.queries.debug),
                #web.post("/tickets/create", self.queries.login),
            ]
        )
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True, expose_headers="*", allow_headers="*",
                )
            },
        )
        for route in list(self.app.router.routes()):
            cors.add(route)

    def start(self):
        web.run_app(self.app, port=self.config.port)

    @web.middleware
    async def error_middleware(self, request, handler):
        try:
            response = await handler(request)
            if response.status < 400:  # if no error coccured
                return response
            message = response.message
            status = response.status

        except web.HTTPException as exception:
            message = exception.reason
            status = 500

        except Exception as exception:
           message = exception.args[0]
           status = 500

        return web.json_response({"error": message}, status=status)