import logging

import bcrypt
from mongoengine import Document, EmbeddedDocument, StringField, EmbeddedDocumentField
import mongoengine

from overlockmqttauth.auth.base import MQTTAuth


logger = logging.getLogger(__name__)


class ACL(EmbeddedDocument):
    """Vernemq 'pattern' match

    Attributes:

        pattern (str): regex to match subscrube/publish ACLs
    """

    pattern = StringField()


class MQTTUser(Document):
    """Vernemq ACL document

    Kept in the same format as vernemq so we don't have to change anything

    https://vernemq.com/docs/configuration/db-auth.html#mongodb

    These fields are used at different points in the 'auth' flow

    Note:

        currently bcrypt version 2a (prefix $2a$) is supported.

    Attributes:

        mountpoint (str): ???
        client_id (str): mqtt client_id
        username (str): mqtt username
        passhash (str): bcrypt hash of password
        publish_acl (list(dict)): list of ACL matches for publishing
        subscribe_acl (list(dict)): list of ACL matches for subscribing
    """

    mountpoint = StringField()
    client_id = StringField()
    username = StringField()
    passhash = StringField()

    publish_acl = EmbeddedDocumentField(ACL)
    subscribe_acl = EmbeddedDocumentField(ACL)

    # Just specify it here so we know what it is for seeding etc.
    meta = {
        "collection": "mqtt_user",
    }

    @classmethod
    def get_by_user(cls, username):
        """Get one by username

        Args:
            username (str): username

        Returns:
            MQTTUser: user in db

        Raises:
            DoesNotExist: No user found
        """

        try:
            auth_doc = MQTTUser.objects(username=username).get()
        except mongoengine.DoesNotExist:
            logger.info("No user '%s' in the database")
            return None

        return auth_doc

    @classmethod
    def check_user_authed(cls, username, password):
        """Try to get a user with the specified username from the database, then
        make sure the password is correct

        Todo:
            Blacklisting - overlock stuff

        Args:
            username (str): username in db
            password (str): plaintext password
        """

        user = cls.get_by_user(username)

        if user is None:
            return None

        return user.password_matches(password)

    def password_matches(self, password):
        match = bcrypt.checkpw(password, self.passhash)
        logger.debug("Password matches: %s", match)
        return match


class VMQAuth(MQTTAuth):
    """Interface to vernemq mongodb auth

    Todo:
        cache blacklists/authenticated status
    """

    @property
    def blacklisted(self):
        # TODO
        # overlock stuff
        return False

    @property
    def authorized(self):
        return MQTTUser.check_user_authed(self._username, self._password)
