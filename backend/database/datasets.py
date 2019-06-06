
from flask_login import current_user
from mongoengine import *
from config import Config

from .tasks import TaskModel

import os
import json

class DatasetModel(DynamicDocument):
    
    id = SequenceField(primary_key=True)
    name = StringField(required=True, unique=True)
    directory = StringField()
    thumbnails = StringField()
    categories = ListField(default=[])

    owner = StringField(required=True)
    users = ListField(default=[])

    annotate_url = StringField(default="")

    default_annotation_metadata = DictField(default={})

    deleted = BooleanField(default=False)
    deleted_date = DateTimeField()

    def save(self, *args, **kwargs):

        directory = os.path.join(Config.DATASET_DIRECTORY, self.name + '/')
        os.makedirs(directory, mode=0o777, exist_ok=True)

        self.directory = directory
        self.owner = current_user.username if current_user else 'system'

        return super(DatasetModel, self).save(*args, **kwargs)

    def get_users(self):
        from .users import UserModel
    
        members = self.users
        members.append(self.owner)

        return UserModel.objects(username__in=members)\
            .exclude('password', 'id', 'preferences')

    def get_locked_annotations(self):
        from . import fix_ids
        from .annotations import AnnotationModel
        from .images import ImageModel

        annotations_locked = []
        images_db = fix_ids(ImageModel.objects(deleted=False, annotated=True, dataset_id=self.id).only(*ImageModel.COCO_PROPERTIES_DB))
        for image in images_db:
            data = {
                'image_info': image,
                'annotations': []
            }
            annotations_db = fix_ids(AnnotationModel.objects(dataset_id=self.id, image_id=image['id'], deleted=False).only(*AnnotationModel.COCO_PROPERTIES_DB))
            for annotation in annotations_db:
                # if 'lock' in annotation['metadata'] and annotation['metadata']['lock']:
                data['annotations'].append(annotation)
            
            annotations_locked.append(data)
            
        return annotations_locked

    def clean_annotations(self):
        from .annotations import AnnotationModel

        AnnotationModel.objects(dataset_id=self.id).delete()

    def import_coco(self, coco_json):

        from workers.tasks import import_annotations

        task = TaskModel(
            name="Import COCO format into {}".format(self.name),
            dataset_id=self.id,
            group="Annotation Import"
        )
        task.save()

        cel_task = import_annotations.delay(task.id, self.id, coco_json)

        return {
            "celery_id": cel_task.id,
            "id": task.id,
            "name": task.name
        }

    def export_coco(self, categories=None, style="COCO"):

        from workers.tasks import export_annotations

        if categories is None or len(categories) == 0:
            categories = self.categories

        task = TaskModel(
            name=f"Exporting {self.name} into {style} format",
            dataset_id=self.id,
            group="Annotation Export"
        )
        task.save()

        cel_task = export_annotations.delay(task.id, self.id, categories)

        return {
            "celery_id": cel_task.id,
            "id": task.id,
            "name": task.name
        }

    def scan(self):

        from workers.tasks import scan_dataset
        
        task = TaskModel(
            name=f"Scanning {self.name} for new images",
            dataset_id=self.id,
            group="Directory Image Scan"
        )
        task.save()
        
        cel_task = scan_dataset.delay(task.id, self.id)

        return {
            "celery_id": cel_task.id,
            "id": task.id,
            "name": task.name
        }

    def is_owner(self, user):

        if user.is_admin:
            return True
        
        return user.username.lower() == self.owner.lower()

    def can_download(self, user):
        return self.is_owner(user)

    def can_delete(self, user):
        return self.is_owner(user)
    
    def can_share(self, user):
        return self.is_owner(user)
    
    def can_generate(self, user):
        return self.is_owner(user)

    def can_edit(self, user):
        return user.username in self.users or self.is_owner(user)
    
    def permissions(self, user):
        return {
            'owner': self.is_owner(user),
            'edit': self.can_edit(user),
            'share': self.can_share(user),
            'generate': self.can_generate(user),
            'delete': self.can_delete(user),
            'download': self.can_download(user)
        }


__all__ = ["DatasetModel"]
