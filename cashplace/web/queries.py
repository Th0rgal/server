from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/btc/new/{coin}")
async def create_ticket(request):
    coin = request.match_info.get("coin").lower()
    if coin == "btc":
        return web.json_response({"address": "0"})
    else:
        return web.json_response({"test": "a"})