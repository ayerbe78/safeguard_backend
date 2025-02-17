from content.views.imports import *
from .email_attach import *


class EmailMessage:
    def __init__(self, msg: MailMessage):
        self.__msg = msg
        self.__id = msg.uid

    @property
    def id(self) -> MailMessage:
        return self.__id

    @property
    def mail(self) -> MailMessage:
        return self.__msg

    @property
    def subject(self) -> str:
        mail: MailMessage = self.mail
        return mail.subject

    @property
    def from_(self) -> str:
        mail: MailMessage = self.mail
        return mail.from_

    @property
    def to(self) -> str:
        mail: MailMessage = self.mail
        return mail.to

    @property
    def text(self) -> str:
        mail: MailMessage = self.mail
        return mail.text

    @property
    def date(self) -> datetime:
        mail: MailMessage = self.mail
        return mail.date

    @property
    def readed(self) -> bool:
        mail: MailMessage = self.mail
        return "\\Seen" in mail.flags

    @property
    def attachs(self) -> list:
        mail: MailMessage = self.mail
        attachs = []
        for idx, att in enumerate(mail.attachments):
            attachs.append(EmailAttach(att, mail.uid, idx))
        return attachs

    def has_flag(self, tag_name: str) -> bool:
        return tag_name in self.mail.flags

    def has_attach(self) -> bool:
        return bool(len(self.attachs))

    def get_dict(self) -> dict:
        messages = [
            {
                "subject": self.subject,
                "messageId": self.mail.headers.get("message-id"),
                "messageId": self.id,
                "description": self.mail.html if self.mail.html.strip() else self.text,
                "sender": {
                    "id": 1,
                    "name": self.mail.from_values.name
                    if self.mail.from_values.name
                    else self.from_.split("@")[0],
                    "email": self.from_,
                    "profilePic": "",
                },
                "to": list(
                    map(
                        lambda a: {
                            "id": 1,
                            "name": a.name,
                            "email": a.email,
                            "profilePic": "",
                        },
                        self.mail.to_values,
                    )
                ),
                "cc": self.mail.cc,
                "bcc": self.mail.bcc,
                "isStarred": self.has_flag(MailMessageFlags.FLAGGED),
                "sentOn": self.date.strftime("%a, %d %b, %Y %I:%M:%S %p"),
            }
        ]
        messages += self.__get_attach_messages()
        messages.reverse()

        return {
            "id": self.id,
            "isChecked": False,
            "subject": self.subject,
            "hasAttachments": bool(len(self.attachs)),
            "isRead": self.readed,
            "messages": messages,
            "cc": self.mail.cc,
            "bcc": self.mail.bcc,
            "isStarred": self.has_flag(MailMessageFlags.FLAGGED),
            "sentOn": self.date,
        }

    def __get_attach_messages(self):
        messages = []
        for a in self.mail.attachments:
            if "message" in a.content_type:
                m = MailMessage.from_bytes(a.payload)
                newMail = {
                    "subject": m.subject,
                    "messageId": m.headers.get("message-id"),
                    "description": m.html if m.html.strip() else m.text,
                    "sender": {
                        "id": 1,
                        "name": m.from_values.name
                        if m.from_values.name
                        else m.from_.split("@")[0],
                        "email": m.from_,
                        "profilePic": "",
                    },
                    "to": list(
                        map(
                            lambda a: {
                                "id": 1,
                                "name": a.name,
                                "email": a.email,
                                "profilePic": "",
                            },
                            m.to_values,
                        )
                    ),
                    "cc": m.cc,
                    "bcc": m.bcc,
                    "isStarred": MailMessageFlags.FLAGGED in m.flags,
                    "sentOn": m.date.strftime("%a, %d %b, %Y %I:%M:%S %p"),
                }
                messages.append(newMail)
        return messages

    def __str__(self) -> str:
        msg = ""
        for k, v in self.get_dict().items():
            msg += f"{k}: {v}\n"
        return msg

    def __repr__(self) -> str:
        return str(self.get_dict())


class EmailMessageDetailed(EmailMessage):
    def get_dict(self) -> dict:
        update = {}
        # update = {
        #     "attach_count": len(self.attachs),
        #     "text": self.text,
        #     "html": self.mail.html,
        # }
        update.update(super().get_dict())
        return update
