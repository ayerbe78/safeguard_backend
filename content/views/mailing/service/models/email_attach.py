from content.views.imports import *


class EmailAttach:
    def __init__(self, attach: MailAttachment, mail_id, pos):
        self.__name = attach.filename
        self.__id = attach.content_id
        self.__content_type = attach.content_type
        self.__size = attach.size
        self.__mail_id = mail_id
        self.__pos = pos

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @property
    def content_type(self):
        return self.__content_type

    @property
    def size(self):
        return self.__size

    @property
    def mail_id(self):
        return self.__mail_id

    @property
    def pos(self):
        return self.__pos

    def __get_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "type": self.content_type,
            "size": self.size,
            "mail_id": self.mail_id,
            "pos": self.pos,
        }

    def __repr__(self) -> dict:
        return str(self.__get_dict())


class EmailAttachFile(EmailAttach):
    def __init__(self, attach: MailAttachment, mail_id, pos):
        super().__init__(attach, mail_id, pos)
        self.__payload = attach.payload

    @property
    def payload(self):
        return self.__payload
