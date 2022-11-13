from .models import DiscussionsLog, Course, Attachments


def add_discussion_log(authors_profile, authors_name, subject, reply_subject, message, course):
    course_obj = Course.objects.get(course_id=course)
    discussion_log = DiscussionsLog.objects.create(authors_profile=authors_profile, authors_name=authors_name,
                                                   subject=subject, reply_subject=reply_subject, message=message,
                                                   course=course_obj)
    discussion_log.save()


def add_course_log(displayname, course_id, shortname, fullname, summary, timemodified):
    try:
        course = Course.objects.get(course_id=course_id)
        if course.timemodified >= timemodified:
            return
        else:
            course.delete()
    except:
        pass

    course_log = Course.objects.create(displayname=displayname, course_id=course_id, shortname=shortname,
                                       fullname=fullname, summary=summary, timemodified=timemodified)
    course_log.save()


def add_attachments(course, filename, fileurl):
    attachment = Attachments.objects.create(file=fileurl, course_id=course, filename=filename)
    attachment.save()


def process_question():
    return 0
