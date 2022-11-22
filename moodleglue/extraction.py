# importing required modules
import PyPDF2
import re
import csv
import io
import requests

from .models import Attachments, Course, ExtractedContexts


def extract_attachment(attachment: Attachments, token, subjectcode):
    related_course = Course.objects.get(course_id=Attachments.course)
    if attachment.file[:-4] == ".pdf":
        header_differentiated = False
        response = requests.get(attachment.file, params={
            "wstoken": token
        })
        on_fly_mem_obj = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(on_fly_mem_obj)

        subject_code = related_course.shortname + "_" + Attachments.filename[:-4]
        new_toc_file = open(subject_code + '.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(new_toc_file)
        fields = ['Topic', 'Page Number', 'Index', 'Heading Order']
        writer.writerow(fields)  # writing header for the table of contents csv object

        # counter for differently specified topics and page numbers
        # to differentiate between main topic and sub-topic
        diffDict = [
            {
                "differentiator": " ",
                "count": []
            },
            {
                "differentiator": "\-",
                "count": []
            },
            {
                "differentiator": ".",
                "count": []
            }
        ]
        littleSpaces = []
        isLittleSpace = False

        contentsObtained = False
        finished = False
        i = 2

        # separating headings into three categories
        headings = []
        second = []
        third = []

        tocIndex = 0  # index for all the contents
        while not contentsObtained or not finished or i > 20:

            pageObj = pdf_reader.getPage(i)

            # extracting text from page
            text = pageObj.extract_text()
            if re.match("([t|T]+(able|ABLE) [o|O]+[f|F] [c|C]+(ontents|ONTENTS))|[c|C]+(ontents|ONTENTS)",
                        text) != None:
                contentsObtained = True
            if (contentsObtained):
                if not header_differentiated and re.findall("[0-9](.[0-9]){0,}", text).__len__() > 10:
                    header_differentiated = True
                toc = re.findall("[0-9a-zA-Z][a-zA-Z0-9’',.)?\- ]+[0-9]",
                                 text)  # finding all the matches for given regular expression i.e finding the lines containing topics and page numbers

                if (toc.__len__() < 2):
                    finished = True
                else:
                    for contents in toc:
                        notDifferentiated = True
                        index = 0
                        filtered = []
                        while (notDifferentiated and index < diffDict.__len__()):
                            diff = "[ " + diffDict[index]['differentiator'] + "]{2,}"
                            filtered = re.split(diff,
                                                contents)  # removing the spaces containing ., - and empty spaces which occurs consecutively and splitting the topics and page numbers
                            if filtered.__len__() == 2 and re.match("^[0-9]{1,3}$", filtered[
                                1]) != None:  # first condition filters the matches which is not containing any page numbers
                                # and the second condition is filtering the matches which contains anything more than numbers of size 1-4 in the page number's section
                                re.match("^[0-9.]", filtered[0])
                                notDifferentiated = False
                                filtered.append(tocIndex)
                                if header_differentiated:
                                    if re.match("[0-9](.[0-9]){2,}", filtered[0]) != None:
                                        filtered.append("2")
                                        # third.append(filtered)
                                    elif re.match("[0-9](.[0-9]){1}", filtered[0]) != None:
                                        filtered.append("1")
                                        # second.append(filtered)
                                    elif re.match("[0-9](.[0-9]){0}", filtered[0]) != None:
                                        filtered.append("0")
                                        # headings.append(filtered)
                                else:
                                    filtered.append("1")
                                    diffDict[index]['count'].append(filtered)
                                writer.writerow(filtered)
                                tocIndex += 1
                            else:
                                index += 1

                        if filtered.__len__() == 1:
                            row = []
                            find_num = re.findall("\s[0-9]{1,3}$", filtered[0])
                            if find_num != None:
                                for splitted in find_num:
                                    # print(splitted)
                                    number_index = filtered[0].index(splitted)
                                    if (number_index + splitted.__len__() == filtered[
                                        0].__len__()):  # making sure the number to be splitted is at last
                                        # because the page number is always given at last
                                        row.append(filtered[0].split(splitted)[0])
                                        row.append(splitted.replace(" ", ""))
                                        row.append(tocIndex)
                                        if header_differentiated:
                                            if re.match("[0-9](.[0-9]){2,}", row[0]) != None:
                                                row.append("2")
                                                # third.append(row)
                                            elif re.match("[0-9](.[0-9]){1}", row[0]) != None:
                                                row.append("1")
                                                # second.append(row)
                                            # elif re.match("[0-9]+(.[0-9]){0}",row[0]) != None:
                                            else:
                                                row.append("0")
                                                # headings.append(row)
                                        else:
                                            row.append("1")
                                            littleSpaces.append(row)
                                        writer.writerow(row)
                                        tocIndex += 1
                                        break
            i += 1

        if not header_differentiated:
            headings = littleSpaces
            for e in diffDict:
                if e['count'].__len__() != 0:
                    if e['count'].__len__() < headings.__len__():
                        third = second
                        second = headings
                        headings = e['count']
                    elif second.__len__() == 0 or second.__len__() > e['count'].__len__():
                        third = second
                        second = e['count']
                    elif third.__len__() == 0 or third.__len__() > e['count'].__len__():
                        third = e['count']

            from tempfile import NamedTemporaryFile
            import shutil

            tempfile = NamedTemporaryFile(mode='w', delete=False)
            with open(subject_code + ".csv", 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=fields)
                writer = csv.DictWriter(tempfile, fieldnames=fields)
                for row in reader:
                    for heading in headings:
                        if row['Index'] == heading[2]:
                            print('updating row', row)
                            row['Heading Order'] = 0
                        row = {'Topic': row['Topic'], 'Page Number': row['Page Number'], 'Index': row['Index'],
                               'Heading Order': row['Heading Order']}
                    extracted = ExtractedContexts.objects.create(topic=row['Topic'], attachment=attachment,
                                                                 page_number=row['Page Number'], index=row['Index'],
                                                                 heading_order=row['Heading Order'], content="")
                    extracted.save()

