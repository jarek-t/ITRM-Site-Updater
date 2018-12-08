# ---------------   Config   ---------------

#Google api key
key = "AIzaSyCd_m2sezcjiGrzn97ngwkrrGrSpKp24KY"
#Style of entry wrapper
entry_style = "style=\"width:21%;display:inline-block;position:relative;min-height:30vh !important;margin-bottom:35%;text-align:center;margin:1.25%;vertical-align:top;padding:1.25%;background-color:#e8e6e4;\""
#Style of entry href
link_style = "style=\"position:absolute;bottom:10%;left:0;right:0;width:30%;margin:auto;padding-top:1.75%;padding-bottom:1.75%;padding-left:7%;padding-right:7%;text-decoration:none;border-radius:15px;background-color:#3c663b;font-size:125%;color:#f2f0ee;vertical-align:bottom;\""
#Path in which to target all .csv files
target_dir = "."

# ---------------  /Config   ---------------

'''
To do:
File name validation
More modularity
Generalize
'''

import os
import sys
import csv
import json
import requests
#-  string -- string  -
#$file_name::$html_entry_conversions
elements = {}
#-  string -- list(list(string))  -
#$file_name::$row_insufficient_for_conversion
skipped_entries = {}

def csv_to_html(fp):
    #Opens target to the first non-header row of data
    f = open(fp, "rt")
    data = csv.reader(f)
    skip_header = next(data)

    #inserted when entries reach a new first letter (export db already sorts)
    alphebetization_header = "<h2 style=\"#3c663b;margin:2.5%;\">{}</h2>\n\n"
    #keeps track of our name's first letter for alphebetization headers
    first_letter = False

    for row in data:
        #Attempts row-HTML conversion, stores if valid
        div = row_to_div(row,fp)
        #Only run onversion if source data is sufficient and original
        if div and div not in elements[fp]:
            #If the first letter of our entries name is different, update then add marker to output
            if (row[4])[0] != first_letter:
                first_letter = (row[4])[0]
                (elements[fp]).append(alphebetization_header.format(first_letter))
            #Add entry to output
            (elements[fp]).append(div)

    #Clean up
    f.close()

def row_to_div(row,fp):
    #row: [0]=url, [1]=zip, [2]=state, [3]=city, [4]=name (12/2/18)
    #          -style                    ||                        name                  ||                cty,st||zip       ||        url            ||               link_style-
    entry = "<div {}>\n<h3 style=\"color:#3c663b;text-align:left;\">{}</h3>\n<h3 style=\"text-align:left;\">{}, {}\n{}</h3>\n<a href=\"http://{}\" target=\"_blank\" {}>{}</a></div>\n\n"
    #                       -style                            ||                                name      ||      url               ||               link_style-
    no_location_entry = "<div {}>\n<h3 style=\"color:#3c663b;text-align:left;margin-bottom:40%;\">{}</h3>\n<a href=\"http://{}\" target=\"_blank\" {}>{}</a></div>\n\n"



    #Skip entries with no company name or website
    if len( row[0] ) == 0 or len( row[4] ) == 0:
        #Adds row to problem-list and returns false to indicate invalidity
        (skipped_entries[fp]).append(row)
        return False
    #Full loction data provided
    elif len(row[1]) > 0 and len(row[2]) > 0 and len(row[3]) > 0:
        return entry.format(entry_style,row[4],row[3],row[2],row[1],row[0],link_style,"Visit")
    #No location data provided
    elif len(row[1]) + len(row[2]) + len(row[3]) == 0:
        return no_location_entry.format(entry_style,row[4],row[0],link_style,"Visit")
    #Partial location data - ZIP code provided
    elif (len(row[2]) == 0 or len(row[3]) == 0) and len(row[1]) > 0:
        #Grabs the city and state from Google's Geocoding api using the ZIP code
        req = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=true&key={}".format(row[1],key))
        location_data = req.json()
        city = location_data["results"][0]["address_components"][1]["short_name"]
        state = location_data["results"][0]["address_components"][2]["short_name"]

        return entry.format(entry_style,row[4],city,state,row[1],row[0],link_style,"Visit")
    #Partial location data - city and state provided
    elif len(row[2]) > 0 and len(row[3]) > 0:
        #Grabs the ZIP code from Google's Geocoding api using the city and state
        req = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={},{}&sensor=true&key={}".format(row[2],row[3],key))
        location_data = req.json()
        zip_ = location_data["results"][0]["address_components"][0]["short_name"]

        return entry.format(entry_style,row[4],row[3],row[2],zip_,row[0],link_style,"Visit")
    #All other cases
    else:
        #Adds row to problem-list and returns false to indicate invalidity
        (skipped_entries[fp]).append(row)
        return False

def export( fp ):
    if not os.path.exists((target_dir+"/out")):
        os.makedirs((target_dir+"/out"))
    if not os.path.exists((target_dir+"/err")):
        os.makedirs((target_dir+"/err"))
    #Create our output and error dump
    exp = open((target_dir+"/out/"+fp[:-4] + "_out.txt"),"w+")
    err = open((target_dir+"/err/"+fp[:-4] + "_err.csv"),"w+")
    #Write parse results
    for elem in elements[fp]:
        exp.write( elem + "\n" )
    #Write errors
    err_export = csv.writer(err)
    err_export.writerows(skipped_entries[fp])
    #Clean up
    exp.close()
    err.close()

def process(fp=False):
    #Get file target file if one isn't passed in
    if not fp:
        fp = input("What file would you like to convert?: \n")
    #Create file's entry in our data
    elements.update({fp:[]})
    skipped_entries.update({fp:[]})
    #Convert then export entries
    csv_to_html(fp)
    export(fp)

def process_all():
    files = os.listdir(target_dir)
    #Process all .csv files in target directory(default program root)
    for f in files:
        if f[-4:] == ".csv":
            print("Processing {}".format(f))
            process(f)

print("---------------------------------------------------------------------\n-ITRM csv-html converter :: 2018 :: Jarek Troyer :: IT Risk Managers-\n---------------------------------------------------------------------")
user_input = "z"
while user_input != "4":
    user_input = str(input("\nEnter a command number:\n1) Convert all .csv in {}...\n2) Enter files to be converted...\n3) Change target_dir...\n4) Exit\n\n>".format(("this directory" if target_dir == "." else target_dir))))
    #Process all files
    if user_input == "1":
        process_all()
    #Process specified files
    elif user_input == "2":
        #Storage for our user-generated file list
        to_be_processed = []
        #Get target files
        print("\nEnter a file (x to quit):\n")
        while user_input != "x":
            user_input = input(">")
            to_be_processed.append(user_input)
        #Process target files
        for fp in to_be_processed:
            process(fp)
    #Change target directory
    elif user_input == "3":
        target_dir = input("\nSet target directory:\n>")
