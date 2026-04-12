from aiohttp import web
import asyncio
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint for Railway monitoring"""
    return web.Response(text="OK", status=200)

async def start_health_server():
    """Start a simple health check server"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    logger.info("Health check server started on port 8000")
    return runner
