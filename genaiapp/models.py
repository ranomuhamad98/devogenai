from django.db import models

# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=200,null=False)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class RightsSupport(models.Model):
            
    class Meta:
        
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model. 
                
        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = ( 
            ('document_extraction', 'global | document extraction'),  
            ('document_translation', 'global | document translation'), 
            ('bank_statement', 'global | bank statement'), 
            ('ktp_extraction', 'global | ktp extraction'), 
            ('image_extraction', 'global | image extraction'), 
            ('dashboard', 'global | dashboard'), 
        )