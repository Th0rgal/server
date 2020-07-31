from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/new')
async def create_ticket(request):
    content = await request.get()
    print(content)