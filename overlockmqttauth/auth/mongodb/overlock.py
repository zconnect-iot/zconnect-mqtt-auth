import mongoengine


class Product(mongoengine.Document):
    iot_name = mongoengine.StringField()


class Project(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    project_keys = mongoengine.ListField(mongoengine.UUIDField())
