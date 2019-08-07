import sys, getopt, csv
import traceback

####
# parses and corrects the foods.csv file.
# this file has a duplicate column entry in the header
####
def parseFooDBCSVFile(inputDir):
    try:
        # get the complete in and output file names
        inFileName = "{0}/foods.csv".format(inputDir)
        outFileName = "{0}/foods.conv.csv".format(inputDir)

        print("Processing input file: {0}\n".format(inFileName))

        # get the input file handle, skip the header line and parse the rest
        with open(inFileName, 'r', encoding='latin_1') as inFH:
            # read a list of lines into data
            data = inFH.readlines()

        # close the input file
        inFH.close()

        # remove the duplicate column name
        data[0] = data[0].replace(',wikipedia_id,wikipedia_id', ',wikipedia_id')

        with open(inFileName, "w", encoding="utf-8") as outFH:
            for el in data:
                output = el.encode('utf-8', 'replace')
                outFH.write(output.decode("utf-8"))

        # close the output file
        outFH.close()

    except Exception as e:
        traceback.print_exc(e)


####
# main entry point to the process
####
if __name__ == "__main__":
    parseFooDBCSVFile('C:/Phil/Work/Informatics/Robokop/FooDB/FooDB_rawdata') #sys.argv[2]
