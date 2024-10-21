from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


from vars import communicator


class MessageContent:
    message_text : str | None
    keyboard_markup : InlineKeyboardMarkup
    
    def __init__(self) -> None:
        self.message_text = ""
        self.keyboard_markup = None


class PagedKeyboard:
    
    def __init__(self, items : list[str] | list[tuple], callback_header : str, with_buttons : bool = False, growth_factor : int = 1) -> None:
        if not isinstance(items, list):
            raise TypeError("Unsupported type of items")
            
        if all(isinstance(i, tuple) for i in items):
            self.items = items
        elif all(isinstance(i, str) for i in items):
            self.items = tuple(enumerate(items))
        else:
            raise TypeError("Unsupported type of items")
        
        self.with_buttons = with_buttons
        self.growth_factor = growth_factor
        self.callback_header = callback_header
        self.previous_button_header = communicator.get_keyboard_title("previous_button")
        self.next_button_header = communicator.get_keyboard_title("next_button")
        self.current_first_point = -1


    def _show(self, next_button : bool = True, previous_button : bool = True) -> MessageContent:
        kb_builder = InlineKeyboardBuilder()
        if self.with_buttons:
            for callback_data, text in self.items[self.current_first_point : (self.current_first_point + self.growth_factor)]:
                kb_builder.button(text = text, callback_data = f"{self.callback_header}={callback_data}")
            
            message_content = MessageContent()
            message_content.message_text = None
            message_content.keyboard_markup = kb_builder.as_markup()
            return message_content

        else:
            message_content = MessageContent()
            for id, text in self.items[self.current_first_point : (self.current_first_point + self.growth_factor)]:
                message_content.message_text += text 

            if previous_button:
                kb_builder.button(text = self.previous_button_header, callback_data=f"{self.callback_header}=previous")

            if next_button:
                kb_builder.button(text = self.next_button_header, callback_data = f"{self.callback_header}=next")

            kb_builder.button(text = communicator.get_keyboard_title("stop_viewing_button"), callback_data=f"{self.callback_header}=stop")
            
            if previous_button and next_button:
                kb_builder.adjust(2, 1)
            else:
                kb_builder.adjust(1, 1)

            message_content.keyboard_markup = kb_builder.as_markup()

            return message_content


    def next(self):
        previous_button = True
        next_button = True
        
        if self.current_first_point == -1:
            self.current_first_point = 0
            previous_button = False
        else:
            self.current_first_point += self.growth_factor
        
        if self.current_first_point + self.growth_factor >= len(self.items):
            next_button = False 

        return self._show(previous_button = previous_button, next_button = next_button)
    

    def previous(self):
        previous_button = True
        if self.current_first_point < self.growth_factor:
            self.current_first_point = 0
        else:
            self.current_first_point -= self.growth_factor
        
        if (self.current_first_point - self.growth_factor) < 0:
            previous_button = False 

        return self._show(previous_button = previous_button) 



