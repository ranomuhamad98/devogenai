from django.db import models
        
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
        )