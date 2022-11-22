from .models import DiscussionsLog, Course, Attachments, ExtractedContexts
import html2text
import requests
import re
from .extraction import extract_attachment

API_URL = "https://api-inference.huggingface.co/models/EnND/bert-qna-custom-tuned"
headers = {"Authorization": "Bearer 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"}


def add_discussion_log(id, authors_profile, authors_name, subject, reply_subject, message, course):
    course_obj = Course.objects.get(course_id=course)
    discussion_log = DiscussionsLog.objects.create(id=id, authors_profile=authors_profile, authors_name=authors_name,
                                                   subject=subject, reply_subject=reply_subject, message=message,
                                                   course=course_obj)
    discussion_log.save()


def update_reply_id(replyid, discussid):
    discussion_log = DiscussionsLog.objects.get(id=discussid)
    discussion_log.replyid = replyid
    discussion_log.save()


def add_course_log(displayname, course_id, shortname, fullname, summary, timemodified):
    try:
        course = Course.objects.get(course_id=course_id)
        if course.timemodified >= timemodified:
            return False
        else:
            course.delete()
    except:
        pass

    course_log = Course.objects.create(displayname=displayname, course_id=course_id, shortname=shortname,
                                       fullname=fullname, summary=summary, timemodified=timemodified)
    course_log.save()
    return True


def like(replyid):
    try:
        discussion = DiscussionsLog.objects.get(replyid=replyid)
        new_like_count = discussion.like_count + 1
        discussion.like_count = new_like_count
        discussion.save()
    except:
        pass


def dislike(replyid):
    try:
        discussion = DiscussionsLog.objects.get(replyid=replyid)
        new_dislike_count = discussion.dislike_count + 1
        discussion.dislike_count = new_dislike_count
        discussion.save()
    except:
        pass


def delete_attachments(course):
    Attachments.objects.filter(course_id=course).delete()


def add_attachments(course, filename, fileurl, token):
    attachment = Attachments.objects.create(file=fileurl, course_id=course, filename=filename)
    attachment.save()
    extract_attachment(attachment, token)


def process_post_message(subject, message, course, token):
    # attachments.file
    text = html2text.html2text(message)
    keywords = [word[1:].replace("_", " ") for word in re.findall(r'\b#\w+', text)]

    course_contexts = ExtractedContexts.objects.filter(course=course)
    selected_contexts = []

    for context in course_contexts:
        if any(key.lower() in context.topic.lower() for key in keywords):
            selected_contexts.append(context)

    if len(selected_contexts) != 0:
        context = selected_contexts[0].content
        return predict_answer(subject, context)
    else:
        return "Bot couldn't find the solution"


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def predict_answer(question, context):
    output = query({
        "inputs": {
            "question": question,
            "context": context
        },
    })
    return output['answer']
