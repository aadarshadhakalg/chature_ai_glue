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
        newTocFile = open(subject_code + '.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(newTocFile)
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
                if not headerDifferentiated and re.findall("[0-9](.[0-9]){0,}", text).__len__() > 10:
                    headerDifferentiated = True
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
                            diff = "[" + diffDict[index]['differentiator'] + " ]{2,}"
                            filtered = re.split(diff,
                                                contents)  # removing the spaces containing ., - and empty spaces which occurs consecutively and splitting the topics and page numbers
                            if filtered.__len__() == 2 and re.match("^[0-9]{1,3}$", filtered[
                                1]) != None:  # first condition filters the matches which is not containing any page numbers
                                # and the second condition is filtering the matches which contains anything more than numbers of size 1-4 in the page number's section
                                notDifferentiated = False
                                filtered.append(tocIndex)
                                if headerDifferentiated:
                                    if re.match("[0-9](.[0-9]){2,}", filtered[0]) != None:
                                        filtered.append("2")
                                        third.append(filtered)
                                    elif re.match("[0-9](.[0-9]){1}", filtered[0]) != None:
                                        filtered.append("1")
                                        second.append(filtered)
                                    # elif re.match("[0-9](.[0-9]){0}",filtered[0]) != None:
                                    else:
                                        filtered.append("0")
                                        headings.append(filtered)
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
                                        if headerDifferentiated:
                                            if re.match("[0-9](.[0-9]){2,}", row[0]) != None:
                                                row.append("2")
                                                third.append(row)
                                            elif re.match("[0-9](.[0-9]){1}", row[0]) != None:
                                                row.append("1")
                                                second.append(row)
                                            # elif re.match("[0-9]+(.[0-9]){0}",row[0]) != None:
                                            else:
                                                row.append("0")
                                                headings.append(row)
                                        else:
                                            row.append("1")
                                            littleSpaces.append(row)
                                        writer.writerow(row)
                                        tocIndex += 1
                                        break
            i += 1

        pageIndex = 0
        firstTopicFound = False
        if not headerDifferentiated:
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

            while not firstTopicFound:
                pageObj = pdf_reader.getPage(i)
                text = pageObj.extract_text()
                text = text.lower()
                # temp = re.split("[0-9]{0,}(.[0-9]){0,}",headings[0],1)
                if text.__contains__(headings[0].lower()):
                    firstTopicFound = True
                    pageIndex = i - headings[1]
                else:
                    i += 1
        else:
            while not firstTopicFound:
                pageObj = pdf_reader.getPage(i)
                text = pageObj.extract_text()
                text = text.lower()
                temp = re.split("[0-9]{0,}(.[0-9]){0,}", headings[0][0], 1)[2]
                temp = temp.lower().replace(" ", "", 1)
                if str(text).__contains__(str(temp)):
                    firstTopicFound = True
                    pageIndex = i - int(headings[0][1])
                else:
                    i += 1

        # closing the csv file object
        newTocFile.close()

        # importing the pandas library
        import pandas as pd
        import numpy as np

        # reading the csv file
        df = pd.read_csv(subject_code + ".csv")

        for j in range(df.__len__()):
            # updating the column value/data
            df.loc[j, 'Page Number'] = str(int(df.loc[j, 'Page Number']) + int(pageIndex))

        df1 = pd.DataFrame(columns=['Context'])
        df = df.join(df1, how="outer")
        context = []
        headingNumber = 0
        subHeadingNumber = 0
        subHeadingContextNumber = 0
        firstHeading = True
        firstSubHeading = True
        first = True
        for k in range(df.__len__() - 1):
            if df.loc[k]['Heading Order'] == 0:
                if not firstHeading:
                    fullContext = ""
                    for f in context:
                        fullContext += " " + f
                    df.loc[df["Index"] == headingNumber, "Context"] = fullContext
                    context = []
                firstHeading = False
                headingNumber = k
            elif df.loc[k]['Heading Order'] == 1:
                if not firstSubHeading:
                    fullContext = ""
                    for f in context[subHeadingContextNumber:]:
                        fullContext += " " + f
                    df.loc[df["Index"] == subHeadingNumber, "Context"] = fullContext
                    subHeadingContextNumber = context.__len__()
                subHeadingNumber = k
                firstSubHeading = False
            else:
                fullContext = ""
                for i in range(int(df.loc[k]['Page Number']), int(df.loc[k + 1]['Page Number']) + 1):
                    ctxpg = pdf_reader.getPage(i)
                    fullContext += " " + ctxpg.extract_text()
                context.append(fullContext)
                df.loc[df["Index"] == k, "Context"] = fullContext

        for i in range(int(df.loc[k + 1]['Page Number']), pdf_reader.getNumPages()):
            ctxpg = pdf_reader.getPage(i)
            fullContext += " " + ctxpg.extract_text()
        context.append(fullContext)
        df.loc[df["Index"] == k, "Context"] = fullContext
        fullContext = ""
        for f in context[subHeadingContextNumber:]:
            fullContext += " " + f
        df.loc[df["Index"] == subHeadingNumber, "Context"] = fullContext
        fullContext = ""
        for f in context:
            fullContext += " " + f
        df.loc[df["Index"] == headingNumber, "Context"] = fullContext

        # writing into the file


        for i in range(df.__len__()):
            extracted = ExtractedContexts.objects.create(topic=df[i]["Topic"], attachment=attachment,
                                                                     page_number=df[i]['Page Number'], index=df[i]['Index'],
                                                                     heading_order=df[i]['Heading Order'], content=df[i]['Context'],course=related_course)
            extracted.save()