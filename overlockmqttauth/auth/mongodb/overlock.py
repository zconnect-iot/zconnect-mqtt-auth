import mongoengine


class Project(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    project_keys = mongoengine.ListField(mongoengine.StringField())
