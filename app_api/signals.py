from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from app_api.functions.services import send_resume_to_docparser

from .models import ResumeFile,Resume
# from .tasks import send_resume_to_api   # this is the worker task



    

@receiver(post_save, sender=ResumeFile)
def resume_file_created(sender, instance, created, **kwargs):
    """
    Signal: fires after ResumeFile is saved
    """
    if not created:
        return

    print(" New ResumeFile created, ID:", instance.id)

    # Call API after DB commit, catch errors so main save never fails
    def call_docparser():
        try:
            docparser_id = send_resume_to_docparser(instance.id)
            if docparser_id:
                # Update Resume table with the returned docparser_id
                resumeid=ResumeFile.objects.filter(id=instance.id).first().resumeid
                print(f" Resume ID: {resumeid}")
                resume = Resume.objects.filter(id=resumeid).first()
                if resume:
                    resume.docparserid = docparser_id
                    resume.save(update_fields=["docparserid"])
                    print(f" Resume {resume.id} updated with docparser_id {docparser_id}")
                else:
                    print(f" No Resume found for ResumeFile ID {instance.id}")
        except Exception as e:
            print(f" Doc parser API failed for ResumeFile {instance.id}: {e}")

    transaction.on_commit(call_docparser)