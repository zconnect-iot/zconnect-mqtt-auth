from mongoengine import Document, EmbeddedDocument, StringField, EmbeddedDocumentField


class VMQACL(EmbeddedDocument):
    """Vernemq 'pattern' match

    Attributes:

        pattern (str): regex to match subscrube/publish ACLs
    """

    pattern = StringField()


class VMQAuth(Document):
    """Vernemq ACL document

    Kept in the same format as vernemq so we don't have to change anything

    https://vernemq.com/docs/configuration/db-auth.html#mongodb

    These fields are used at different points in the 'auth' flow

    Attributes:

        mountpoint (str): ???
        client_id (str): mqtt client_id
        username (str): mqtt usernam
        passhash (str): bcrypt hash of password
        publish_acl (list(dict)): list of ACL matches for publishing
        subscribe_acl (list(dict)): list of ACL matches for subscribing
    """

    mountpoint = StringField()
    client_id = StringField()
    username = StringField()
    passhash = StringField()

    publish_acl = EmbeddedDocumentField(VMQACL())
    subscribe_acl = EmbeddedDocumentField(VMQACL())
