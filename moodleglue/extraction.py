# importing required modules
import PyPDF2
import re
import csv
import io
import requests
# importing the pandas library
import pandas as pd
import numpy as np

from .models import Attachments, Course, ExtractedContexts


def extract_attachment(attachment: Attachments, token):
    print(attachment.course)
    related_course = Course.objects.get(course_id=attachment.course.course_id)
    if attachment.filename[-4:] == ".pdf":
        header_differentiated = False
        response = requests.get(attachment.file, params={
            "token": token
        })
        on_fly_mem_obj = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(on_fly_mem_obj)

        subject_code = related_course.shortname + "_" + attachment.filename[:-4]
        new_toc_file = open(subject_code + '.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(new_toc_file)
        fields = ['Topic', 'Page Number', 'Index', 'Heading Order']
        writer.writerow(fields)  # writing header for the table of contents csv object

        # counter for differently specified topics and page numbers
        # to differentiate between main topic and sub-topic
        diff_dict = [
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
        little_spaces = []
        is_little_space = False

        contents_obtained = False
        finished = False
        i = 2

        # separating headings into three categories
        headings = []
        second = []
        third = []

        toc_index = 0  # index for all the contents
        while not contents_obtained or not finished or i > 20:

            page_obj = pdf_reader.getPage(i)

            # extracting text from page
            text = page_obj.extract_text()
            if re.match("([t|T]+(able|ABLE) [o|O]+[f|F] [c|C]+(ontents|ONTENTS))|[c|C]+(ontents|ONTENTS)",
                        text) != None:
                contents_obtained = True
            if contents_obtained:
                if not header_differentiated and re.findall("[0-9](.[0-9]){0,}", text).__len__() > 10:
                    header_differentiated = True
                toc = re.findall("[0-9a-zA-Z][a-zA-Z0-9’',.)?\- ]+[0-9]",
                                 text)  # finding all the matches for given regular expression i.e finding the lines containing topics and page numbers

                if toc.__len__() < 2:
                    finished = True
                else:
                    for contents in toc:
                        not_differentiated = True
                        index = 0
                        filtered = []
                        while not_differentiated and index < diff_dict.__len__():
                            diff = "[" + diff_dict[index]['differentiator'] + " ]{2,}"
                            filtered = re.split(diff,
                                                contents)  # removing the spaces containing ., - and empty spaces which occurs consecutively and splitting the topics and page numbers
                            if filtered.__len__() == 2 and re.match("^[0-9]{1,3}$", filtered[
                                1]) != None:  # first condition filters the matches which is not containing any page numbers
                                # and the second condition is filtering the matches which contains anything more than numbers of size 1-4 in the page number's section
                                not_differentiated = False
                                filtered.append(toc_index)
                                if header_differentiated:
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
                                    diff_dict[index]['count'].append(filtered)
                                writer.writerow(filtered)
                                toc_index += 1
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
                                        row.append(toc_index)
                                        if header_differentiated:
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
                                            little_spaces.append(row)
                                        writer.writerow(row)
                                        toc_index += 1
                                        break
            i += 1

        page_index = 0
        first_topic_found = False
        if not header_differentiated:
            headings = little_spaces
            for e in diff_dict:
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

            while not first_topic_found:
                page_obj = pdf_reader.getPage(i)
                text = page_obj.extract_text()
                text = text.lower()
                # temp = re.split("[0-9]{0,}(.[0-9]){0,}",headings[0],1)
                if text.__contains__(headings[0].lower()):
                    first_topic_found = True
                    page_index = i - headings[1]
                else:
                    i += 1
        else:
            while not first_topic_found:
                page_obj = pdf_reader.getPage(i)
                text = page_obj.extract_text()
                text = text.lower()
                temp = re.split("[0-9]{0,}(.[0-9]){0,}", headings[0][0], 1)[2]
                temp = temp.lower().replace(" ", "", 1)
                if str(text).__contains__(str(temp)):
                    first_topic_found = True
                    page_index = i - int(headings[0][1])
                else:
                    i += 1

        # closing the csv file object
        new_toc_file.close()

        # reading the csv file
        df = pd.read_csv(subject_code + ".csv")

        for j in range(df.__len__()):
            # updating the column value/data
            df.loc[j, 'Page Number'] = str(int(df.loc[j, 'Page Number']) + int(page_index))

        df1 = pd.DataFrame(columns=['Context'])
        df = df.join(df1, how="outer")
        context = []
        heading_number = 0
        sub_heading_number = 0
        sub_heading_context_number = 0
        first_heading = True
        first_sub_heading = True
        first = True
        for k in range(df.__len__() - 1):
            if df.loc[k]['Heading Order'] == 0:
                if not first_heading:
                    full_context = ""
                    for f in context:
                        full_context += " " + f
                    df.loc[df["Index"] == heading_number, "Context"] = full_context
                    context = []
                    first_sub_heading = True
                    sub_heading_context_number = 0
                first_heading = False
                heading_number = k
            elif df.loc[k]['Heading Order'] == 1:
                if df.loc[k + 1]['Heading Order'] != 2:
                    if str(df.loc[sub_heading_number]['Context']) == "nan" or df.loc[sub_heading_number]['Context'] == "":
                        full_context = ""
                        for f in context[sub_heading_context_number:]:
                            full_context += " " + f
                        df.loc[df["Index"] == sub_heading_number, "Context"] = full_context
                        sub_heading_context_number = context.__len__()
                    full_context = ""
                    for i in range(int(df.loc[k]['Page Number']), int(df.loc[k + 1]['Page Number']) + 1):
                        ctxpg = pdf_reader.getPage(i)
                        full_context += " " + ctxpg.extract_text()
                    full_context.replace("\n", " ")
                    context.append(full_context)
                    df.loc[df["Index"] == k, "Context"] = full_context
                    sub_heading_context_number = context.__len__()
                else:
                    if df.loc[k]['Page Number'] != df.loc[k + 1]['Page Number']:
                        for i in range(int(df.loc[k]['Page Number']), int(df.loc[k + 1]['Page Number'])):
                            ctxpg = pdf_reader.getPage(i)
                            full_context += " " + ctxpg.extract_text()
                        full_context.replace("\n", " ")
                        context.append(full_context)
                    if not first_sub_heading:
                        full_context = ""
                        for f in context[sub_heading_context_number:]:
                            full_context += " " + f
                        df.loc[df["Index"] == sub_heading_number, "Context"] = full_context
                        sub_heading_context_number = context.__len__()
                    sub_heading_number = k
                    first_sub_heading = False
            else:
                full_context = ""
                for i in range(int(df.loc[k]['Page Number']), int(df.loc[k + 1]['Page Number']) + 1):
                    ctxpg = pdf_reader.getPage(i)
                    full_context += " " + ctxpg.extract_text()
                full_context.replace("\n", " ")
                context.append(full_context)
                df.loc[df["Index"] == k, "Context"] = full_context

        for i in range(int(df.loc[k + 1]['Page Number']), pdf_reader.getNumPages()):
            ctxpg = pdf_reader.getPage(i)
            full_context += " " + ctxpg.extract_text()
        full_context.replace("\n", " ")
        context.append(full_context)
        df.loc[df["Index"] == k, "Context"] = full_context
        full_context = ""
        for f in context[sub_heading_context_number:]:
            full_context += " " + f
        df.loc[df["Index"] == sub_heading_number, "Context"] = full_context
        full_context = ""
        for f in context:
            full_context += " " + f
        df.loc[df["Index"] == heading_number, "Context"] = full_context
        df = df.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n', ' ', regex=True)

        # writing into the file

        for i in range(df.__len__()):
            extracted = ExtractedContexts.objects.create(topic=df["Topic"].values[i], attachment=attachment,
                                                         page_number=df["Page Number"].values[i], index=df["Index"].values[i],
                                                         heading_order=df["Heading Order"].values[i], content=df["Context"].values[i],
                                                         course=related_course)
            extracted.save()
