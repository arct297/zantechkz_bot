from .sections.general.general_section import general_router
from .sections.bot_admin.bot_admin_section import admin_router

routers = (
    general_router, 
    admin_router, 
)
