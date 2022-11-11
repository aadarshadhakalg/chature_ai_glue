# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
import requests

baseurl = "http://20.204.221.147/webservice/rest/server.php"


class ProcessDiscussionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, format=None):
        post_id = request.data['post_id']
        token = request.data['token']
        course_id = request.data['course']
        self.get_post_detail(post_id,token,course_id)
        return Response(status=status.HTTP_200_OK)

    def get_post_detail(self, post_id, token, course_id):
        response = requests.get(
            f"{baseurl}?wstoken={token}&wsfunction=mod_forum_get_discussion_post&moodlewsrestformat=json",params={
                    "postid":post_id,
                })
        
        if response.status_code == 200:
            subject = response.json()["post"]["subject"]
            message = response.json()["post"]["message"]
            reply_subject = response.json()["post"]["replysubject"]
            reply_message = self.process_post(subject, message, course_id, token)
            self.reply(reply_message, reply_subject, token, post_id)

    def process_post(self, subject, message, course, token):
        return "Bot noticed this discussion"

    def reply(self, message, subject, token, postid):
        response = requests.get(
            f"{baseurl}?wstoken={token}&wsfunction=mod_forum_add_discussion_post&moodlewsrestformat=json", params={
                "postid": postid,
                "subject": subject,
                "message": message,
            })
        print(response.status_code)
