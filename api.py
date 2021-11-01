from aiohttp import web
from .db import DataBase

async def getKeyword(request):
    """
    API endpoint to return information about a specific keyword.
    """
    db = request.app['db']
    keyword = request.match_info.get('keyword')
    return web.json_result(db.getKeywordDetails(keyword))

async def getKeywords(request):
    """
    API endpoint to return all known keywords.
    """
    db = request.app['db']

    return web.json_result(db.getKeywords())


if __name__=="__main__":
    try:
        # initilize server
        app = web.Application()
        app.add_routes([
            web.get('/{keyword}', getKeyword),
            web.get('/keywords', getKeywords)
        ])

        # initialize database
        db = DataBase()
        app['db'] = db

        # run server
        web.run_app(app)
    except KeyboardInterrupt:
        db.close()