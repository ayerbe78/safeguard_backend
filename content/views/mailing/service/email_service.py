from content.views.imports import *
from .models.email_message import *
from .models import *

from imap_tools.utils import Iterable


class EmailService:
    def __init__(
        self,
        email: str,
        passw: str,
        server: str = settings.EMAIL_HOST,
        imap_port: int = 993,
        trash_folder="Trash",
        sent_folder="Sent",
        stmp_port=465,
        user_name="",
    ):
        self.__email = email
        self.__passw = passw
        self.__server = server
        self.__imap_port = imap_port
        self.__stmp_port = stmp_port
        self.__trash_folder = trash_folder
        self.__sent_folder = sent_folder
        self.__date_format = "%a, %d %b %Y %H:%M:%S +0000 (GMT)"
        self.__user_name = user_name if user_name else email.split("@")[0]

    def get_messages(
        self,
        offset=0,
        limit=50,
        desc=True,
        folder: str = "",
        mark_seen=False,
        headers_only=False,
        flag=None,
    ):
        with self.__get_mailbox(folder) as mailbox:
            emails = []
            criteria = A(keyword=flag) if flag else "All"
            for msg in mailbox.fetch(
                criteria,
                limit=slice(offset, offset + limit),
                reverse=desc,
                mark_seen=mark_seen,
                headers_only=headers_only,
            ):
                emails.append(EmailMessage(msg))

            return emails

    def get_message(self, message_id, folder: str = "", mark_seen=False):
        mail = self.__get_message_value(message_id, folder, mark_seen)
        return EmailMessageDetailed(mail) if mail else None

    def get_folder_dir(self, folder="", get_stats=True):
        with self.__get_mailbox(folder) as mailbox:
            raw_folders = mailbox.folder.list(folder)
            folders = []
            for f in raw_folders:
                item = {"name": f.name}
                if get_stats:
                    stat = mailbox.folder.status(f"{folder}/{f.name}")
                    item["stats"] = stat
                folders.append(item)
            return folders

    def get_folder_count(self, folder="", flag=None):
        count = 0
        if folder == "":
            return count
        if flag:
            with self.__get_mailbox(folder) as mailbox:
                _, mails = mailbox.uids(A(keyword=flag))
                count = len(mails)

        else:
            with self.__get_mailbox(folder) as mailbox:
                stat = mailbox.folder.status(
                    folder,
                )
                count = stat["MESSAGES"]

        return count

    def get_message_attach(self, message_id, attach_pos, folder="", mark_seen=False):
        mail = self.__get_message_value(message_id, folder, mark_seen)
        if mail is None:
            return None
        else:
            selected_attach = mail.attachments[attach_pos]
            return EmailAttachFile(selected_attach, message_id, attach_pos)

    def move_message(self, msg_ids, from_folder="", to_folder=""):
        with self.__get_mailbox(from_folder) as mailbox:
            result = mailbox.move(msg_ids, to_folder)
            return True

    def delete_message(self, msg_ids, folder="", soft=True):
        if soft and folder.lower() != self.__trash_folder.lower():
            return self.move_message(msg_ids, folder, self.__trash_folder)
        else:
            with self.__get_mailbox(folder) as mailbox:
                mailbox.delete(msg_ids)
                return True

    def tag_message(self, msg_ids, tags, folder="", remove=False):
        with self.__get_mailbox(folder) as mailbox:
            response = mailbox.flag(msg_ids, tags, not remove)
            return True

    def toggle_seen_message(self, msg_ids, seen: bool = True, folder=""):
        return self.tag_message(msg_ids, (MailMessageFlags.SEEN), folder, not seen)

    def toggle_fav_message(self, msg_ids, fav: bool = True, folder=""):
        return self.tag_message(msg_ids, (MailMessageFlags.FLAGGED), folder, not fav)

    def send_message(self, to_addr, subject, reply, cc, bcc, text="", html=""):
        today = self.__get_local_time(string=True)
        message = MIMEMultipart()
        message["From"] = f"{self.__user_name} <{self.__email}>"
        message["To"] = to_addr
        message["Subject"] = subject
        message["Date"] = today
        if reply:
            message["reply-to"] = reply
        if html:
            message.attach(MIMEText(html, "html"))
        return self.__send_message(message, to_addr, cc, bcc)

    def reply_message(self, message_id, cc, bcc, folder="", html="", text=""):
        mail = self.__get_message_value(message_id, folder)
        original = self.__get_original_mail(mail)
        today = self.__get_local_time(string=True)
        new = MIMEMultipart()

        new["Message-ID"] = make_msgid()
        new["In-Reply-To"] = original["Message-ID"]
        new["References"] = original["Message-ID"]
        new["Subject"] = "Re: " + original["Subject"]
        new["To"] = original["Reply-To"] or original["From"]
        new["From"] = f"{self.__user_name} <{self.__email}>"
        new["Date"] = today
        new.attach(MIMEText(html, "html"))
        if not text:
            f = HTMLFilter()
            f.feed(html)
            text = f.text
        new.attach(MIMEText(text, "plain"))
        new.attach(MIMEMessage(original))

        return self.__send_message(new, new["To"], cc, bcc)

    def check_connection(self):
        try:
            with self.__get_mailbox() as mailbox:
                mailbox.folder.list()
                return True
        except:
            return False

    def __send_message(self, message: MIMEMultipart, to_addr, cc, bcc):
        with smtp.SMTP_SSL(self.__server, self.__stmp_port) as server:
            server.login(self.__email, self.__passw)
            if bcc:
                server.sendmail(
                    self.__email,
                    self.__blind_mail_sending_addresses(bcc),
                    message.as_string(),
                )
                message["Bcc"] = bcc
            if cc:
                message["Cc"] = cc
            server.sendmail(
                self.__email,
                self.__mail_sending_addresses(to_addr, cc),
                message.as_string(),
            )
        msg = message.as_bytes()

        with self.__get_mailbox() as mailbox:
            response = mailbox.append(
                msg,
                self.__sent_folder,
                dt=self.__get_local_time(),
                flag_set=[MailMessageFlags.SEEN],
            )
            return True

    def __get_original_mail(self, mail: MailMessage):
        original = mail.obj
        for part in original.walk():
            if part.get("Content-Disposition") and part.get(
                "Content-Disposition"
            ).startswith("attachment"):

                part.set_type("text/plain")
                part.set_payload(
                    "Attachment removed: %s (%s, %d bytes)"
                    % (
                        part.get_filename(),
                        part.get_content_type(),
                        len(part.get_payload(decode=True)),
                    )
                )
                del part["Content-Disposition"]
                del part["Content-Transfer-Encoding"]
        return original

    def __blind_mail_sending_addresses(self, bcc: str):
        addresses = bcc.split(",") if bcc else []
        addresses_stripped = list(map(lambda a: a.strip(), addresses))
        return addresses_stripped

    def __mail_sending_addresses(self, to: str, cc: str):
        to_addresses = to.split(",") if to else []
        to_addresses_stripped = list(map(lambda a: a.strip(), to_addresses))
        cc_addresses = cc.split(",") if cc else []
        cc_addresses_stripped = list(map(lambda a: a.strip(), cc_addresses))
        addresses = to_addresses_stripped + cc_addresses_stripped
        return addresses

    def __get_message_value(
        self, message_id, folder: str = "", mark_seen=False
    ) -> MailMessage:
        with self.__get_mailbox(folder) as mailbox:
            mails = list(mailbox.fetch(
                A(uid=str(message_id)), mark_seen=mark_seen))
            return mails[0] if len(mails) else None

    def __get_mailbox(self, folder_name=None) -> MailBox:
        if folder_name is None or folder_name == "":
            folder_name = "INBOX"
        return MailBox(self.__server, self.__imap_port).login(
            self.__email, self.__passw, folder_name
        )

    def __get_local_time(self, string=False):
        date = datetime.now(pytz.utc)
        if string:
            date = date.strftime(self.__date_format)
        return date

    def __check_response(self, response):
        pass
