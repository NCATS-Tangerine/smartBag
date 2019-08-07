import traceback
import sys
import csv

####
# parses and corrects the FooDB files by fixing the column header in foods.csv file and insuring only ascii characters

####
def parseFooDBCSVFile(inFileName):
    try:
        print("Processing input file: {0}\n".format(inFileName))

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
                outFH.write(el.encode('ascii', 'replace').decode('ascii', 'replace'))

        # close the output file
        outFH.close()


        with open(inFileName, 'r', encoding='ISO-8859-1') as stream:
            reader = csv.reader (stream)

            headers = next (reader)

            for row in reader:
               values = [ r for r in row ]

               if len(headers) != len(values):
                    print(values)
                    for i, v in enumerate(values):
                        print(f" {i} - {v}")

    except Exception as e:
        traceback.print_exc(e)


####
# main entry point to the process
####
if __name__ == "__main__":
    parseFooDBCSVFile(sys.argv[2]) # 'C:/Phil/Work/Informatics/Robokop/FooDB/FooDB_rawdata/foods.csv' sys.argv[2]
