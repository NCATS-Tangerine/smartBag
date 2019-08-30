import traceback
import sys
import csv

####
# parses and corrects the FooDB files by fixing the column header in foods.csv file and insuring only ascii characters

####
def parseFooDBCSVFile(inFileName):
    try:
        print("Processing input file: {0} to remove invalid characters\n".format(inFileName))

        # get the input file handle, skip the header line and parse the rest
        with open(inFileName, 'r', encoding='latin_1') as inFH:
            # read a list of lines into data
            data = inFH.readlines()

        # close the input file
        inFH.close()

        # remove the duplicate column name
        data[0] = data[0].replace(',wikipedia_id,wikipedia_id', ',wikipedia_id,picture_file_name')

        with open(inFileName, "w", encoding="utf-8") as outFH:
            for el in data:
                outFH.write(el.encode('ascii', 'replace').decode('ascii', 'replace').replace('\\\\', '').replace('\\"', ''))

        # close the output file
        outFH.close()

        # the contents.csv file needs special handling to remove records that are undesirable
        if "contents" in inFileName:
            print("Processing input file: {0} to remove undesirable rows\n".format(inFileName))

            # get the input file handle, read the header line and parse the rest
            with open(inFileName, 'r', encoding='latin_1') as inFH:
                # read a list of lines into data
                rows = csv.reader(inFH)

                # get the header row
                header_line = next(rows)

                # get indexes to the elements to be inspected
                citation_index = header_line.index('citation')
                standard_content_index = header_line.index('standard_content')

                # create a array for row records
                out_rows = []

                # save the data header
                out_rows.append(header_line)

                # for each element replace all the non UTF-8 characters
                for row in rows:
                    if row[citation_index] != "MANUAL" and (row[standard_content_index] == 'NULL' or row[standard_content_index] == None or float(row[standard_content_index]) > 0):
                        # save the row to the final output array
                        out_rows.append(row)

            # close the input file
            inFH.close()

            # write out the repaired rows
            with open(inFileName, "w", encoding="utf-8") as outFH:
                # get a csv file writer
                writer = csv.writer(outFH)

                # output all rows
                writer.writerows(out_rows)

            # close the output file
            outFH.close()

    except Exception as e:
        traceback.print_exc(e)


####
# main entry point to the process
####
if __name__ == "__main__":
    parseFooDBCSVFile(sys.argv[2]) # contents foods 'C:/Phil/Work/Informatics/Robokop/FooDB/FooDB_rawdata/ - Copy.csv'
