from .main_keyboard import create_keyboard_by_access

from .bot_admins_kb import generate_content_type_choose_kb_builder
content_type_choose_kb = generate_content_type_choose_kb_builder().as_markup()

from .paging_kb import PagedKeyboard