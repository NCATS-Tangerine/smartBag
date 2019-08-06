import sys, getopt, csv


####
# parses and corrects the foods.csv file.
# this file has a duplicate column entry in the header
####
def parseFooDBCSVFile(inputDir):
    try:
        # get the complete in and output file names
        inFileName = "{0}/foods.csv".format(inputDir)

        print("Processing input file: {0}\n".format(inFileName))

        # get the input file handle, skip the header line and parse the rest
        with open(inFileName, 'r') as inFH:
            # read a list of lines into data
            data = inFH.readlines()

            # remove the duplicate column name
            data[0] = data[0].replace(',wikipedia_id,wikipedia_id', ',wikipedia_id')

        # close the input file
        inFH.close()

        # open the file again for writing
        with open(inFileName, 'w') as outFH:
            outFH.writelines(data)

        # close the output file
        outFH.close()

    except Exception as e:
        print("Error: {0}".format(e))


####
# main entry point to the process
####
if __name__ == "__main__":
    parseFooDBCSVFile(sys.argv[1])
