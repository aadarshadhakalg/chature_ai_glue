from .models import DiscussionsLog, Course, Attachments


def add_discussion_log(authors_profile, authors_name, subject, reply_subject, message, course):
    discussion_log = DiscussionsLog.objects.create(authors_profile=authors_profile, authors_name=authors_name,
                                                   subject=subject, reply_subject=reply_subject, message=message,
                                                   course=course)
    discussion_log.save()


def add_course_log(displayname, course_id, shortname, fullname, summary):
    course_log = Course.objects.create(displayname=displayname, course_id=course_id, shortname=shortname,
                                       fullname=fullname, summary=summary)
    course_log.save()


def add_attachments(course, filename, fileurl):
    attachment = Attachments.objects.create(file=fileurl, course_id=course, filename=filename)
    attachment.save()


def process_question():
    return 0
