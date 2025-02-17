from content.models import EmptyPaymentLogEntry, Client, ClientLog
import logging

logger = logging.getLogger("django")


def log_empty_payment(data):
    try:
        EmptyPaymentLogEntry.objects.create(**data)
        return True
    except Exception as e:
        logger.error("An error occurred when logging zero payment", e)
        return False


class ClientLogging:
    """
    A class used to log events related to Client actions.
    """

    def log_client_insert(self, user, client_id):
        """
        Log the insertion of a new client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being inserted.
        """
        self.__add_entry("insert", client_id, user, "Inserted as a new Client")

    def log_application_insert(self, user, application_id):
        """
        Log the insertion of a new client.

        Args:
            user: The user performing the action.
            application_id: The ID of the application being inserted.
        """
        self.__add_entry("insert", application_id, user,
                         "Inserted as a new Application")

    def log_client_update(self, user, client_id, client=None):
        """
        Log the update of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being updated.
        """
        self.__add_entry("update", client_id, user,
                         self.__obtain_important_data(client))

    def log_client_delete(self, user, client_id):
        """
        Log the deletion of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being deleted.
        """
        self.__add_entry("delete", client_id, user, "Deleted Client")

    def log_client_migrate(self, user, client_id, description=""):
        """
        Log the migration of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being migrated.
        """
        self.__add_entry("migrate", client_id, user,
                         description)

    def log_client_transfer(self, user, client_id):
        """
        Log the transfer of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being transferred.
        """
        self.__add_entry("transfer", client_id, user,
                         "Transfered from Application to Client")

    def log_app_transfer(self, user, client_id, message):
        """
        Log the transfer of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client being transferred.
        """
        self.__add_entry("transfer", client_id, user,
                         message)

    def log_client_check_toggle(self, user, client_id):
        """
        Log the toggle check of a client.

        Args:
            user: The user performing the action.
            client_id: The ID of the client for which the check is being toggled.
        """
        self.__add_entry("check_toggle", client_id, user)

    def __get_client(self, client_id):
        """
        Retrieve a client object by its ID.

        Args:
            client_id: The ID of the client.

        Returns:
            The client object if found, otherwise None.
        """
        try:
            client = Client.objects.get(id=client_id)
        except:
            client = None
        return client

    def __add_entry(self, type, client_id, user, description="Empty"):
        """
        Add a log entry for the given action, client, and user.

        Args:
            type: The type of action performed (e.g., "insert", "update", "delete").
            client_id: The ID of the client.
            user: The user performing the action.
        """
        client = self.__get_client(client_id)
        data = dict(
            type=type,
            user=user,
            client=client,
            description=description
        )
        ClientLog.objects.create(**data)

    def __obtain_important_data(self, client: Client):
        return f"""agent: {client.id_agent}, insurance: {client.id_insured}, state: {client.id_state}, subscriberid: {client.suscriberid}, effective_date: {client.aplication_date}
        """
