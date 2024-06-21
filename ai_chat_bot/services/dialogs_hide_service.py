import typing

from ai_chat_bot.model.dialog_data import DialogData


class DialogHideService:
    def __init__(self, id_not_to_hide: str):
        self.id_not_to_hide = id_not_to_hide

    def hide(self, dialog: DialogData) -> DialogData:
        if str(dialog.id) != self.id_not_to_hide:
            dialog.name = self.new_name(dialog.name)
        return dialog

    def new_name(self, name:str):
        if len(name) < 2: return '_' * 2
        return name[:1] + '_' * (len(name)-1)
