# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
import  json
import requests
from .helpers import add_attachments, add_discussion_log, add_course_log

baseurl = "http://20.204.221.147/webservice/rest/server.php"


class ProcessDiscussionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, format=None):
        post_id = request.data['post_id']
        token = request.data['token']
        course_id = request.data['course']
        self.get_course_attachments(course_id=course_id, token=token)
        self.get_post_detail(post_id, token, course_id)
        return Response(status=status.HTTP_200_OK)

    def get_post_detail(self, post_id, token, course_id):
        response = requests.get(
            baseurl, params={
                "postid": post_id,
                "wstoken": token,
                "wsfunction": "mod_forum_get_discussion_post",
                "moodlewsrestformat": "json",
            })

        if response.status_code == 200:
            subject = response.json()["post"]["subject"]
            message = response.json()["post"]["message"]
            reply_subject = response.json()["post"]["replysubject"]
            authors_name = response.json()["post"]["author"]["fullname"]
            authors_name = response.json()["post"]["author"]["urls"]["profile"]
            reply_message = self.process_post(subject, message, course_id, token)

            add_discussion_log(authors_name=authors_name, subject=subject, reply_subject=reply_subject, message=message,
                               course=course_id)

            self.reply(reply_message, reply_subject, token, post_id)

    def process_post(self, subject, message, course, token):
        return "Bot noticed this discussion"

    def reply(self, message, subject, token, postid):
        response = requests.get(
            baseurl, params={
                "postid": postid,
                "subject": subject,
                "message": message,
                "wstoken": token,
                "wsfunction": "mod_forum_add_discussion_post",
                "moodlewsrestformat": "json",
            })
        print(response.status_code)

    def get_course_attachments(self, course_id, token):
        course_detail = requests.get(baseurl, params={
            "wstoken": token,
            "wsfunction": "core_course_get_courses",
            "options[ids][0]": course_id,
            "moodlewsrestformat": "json",

        })
        print(course_detail.json())
        if course_detail.status_code == 200:
            shortname = course_detail.json()[0]['shortname']
            fullname = course_detail.json()[0]['fullname']
            displayname = course_detail.json()[0]['fullname']
            summary = course_detail.json()[0]['summary']
            timemodified = course_detail.json()[0]['timemodified']

            add_course_log(course_id=course_id, shortname=shortname, fullname=fullname, displayname=displayname,
                           summary=summary,timemodified=timemodified)

        course_contents = requests.get(baseurl, params={
            "wstoken": token,
            "wsfunction": " core_course_get_contents",
            "moodlewsrestformat": "json",
            "course_id":course_id,
        })

        if course_contents.status_code == 200:
            sections = course_contents.json()
            print(sections)

            for section in sections:
                name = section["name"]
                modules = section["modules"]

                for module in modules:
                    contents = module["contents"]
                    if contents is None:
                        contents = []

                    for content in contents:
                        if content['type'] == "file":
                            filename = content['filename']
                            fileurl = content['fileurl']

                            add_attachments(course=course_id,filename=filename,fileurl=fileurl)
