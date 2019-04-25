import sys, getopt

# debug use only
test_tissues={
"Adipose_Subcutaneous, 0002190"
}

# list of all the tissues in the GTEX data
tissues={
"Adipose_Subcutaneous,0002190",
"Adipose_Visceral_Omentum,0003688",
"Adrenal_Gland,0018303",
"Artery_Aorta,0004178",
"Artery_Coronary,0002111",
"Artery_Tibial,0007610",
"Brain_Amygdala,0001876",
"Brain_Anterior_cingulate_cortex_BA24,0006101",
"Brain_Caudate_basal_ganglia,0002420",
"Brain_Cerebellar_Hemisphere,0002245",
"Brain_Cerebellum,0002037",
"Brain_Cortex,0000956",
"Brain_Frontal_Cortex_BA9,0001870",
"Brain_Hippocampus,0002310",
"Brain_Hypothalamus,0001898",
"Brain_Nucleus_accumbens_basal_ganglia,0001882",
"Brain_Putamen_basal_ganglia,0001874",
"Brain_Spinal_cord_cervical_c-1,0002726",
"Brain_Substantia_nigra,0002038",
"Breast_Mammary_Tissue,0001911",
"Cells_EBV-transformed_lymphocytes,0001744",
"Cells_Transformed_fibroblasts,0015764",
"Colon_Sigmoid,0001159",
"Colon_Transverse,0001157",
"Esophagus_Gastroesophageal_Junction,0007650",
"Esophagus_Mucosa,0002469",
"Esophagus_Muscularis,0004648",
"Heart_Atrial_Appendage,0006618",
"Heart_Left_Ventricle,0002084",
"Liver,0002107",
"Lung,0002048",
"Minor_Salivary_Gland,0001830",
"Muscle_Skeletal,0001134",
"Nerve_Tibial,0001323",
"Ovary,0000992",
"Pancreas,0001264",
"Pituitary,0000007",
"Prostate,0002367",
"Skin_Not_Sun_Exposed_Suprapubic,0036149",
"Skin_Sun_Exposed_Lower_leg,0004264",
"Small_Intestine_Terminal_Ileum,0002116",
"Spleen,0002106",
"Stomach,0000945",
"Testis,0000473",
"Thyroid,0002046",
"Uterus,0000995",
"Vagina,0000996",
"Whole_Blood,0000178"}

####
# processes each CSV file
####
def processCSVFiles(argv):
    inputDir = ''
    outputDir = ''
    
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["idir=","odir="])
    except getopt.GetoptError:
        print("parseGTExCSV.py -i <inputDir> -o <outputDir>")
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print("parseGTExCSV.py -i <inputDir> -o <outputDir>")
            sys.exit()
        elif opt in ("-i", "--idir"):
            inputDir = arg
        elif opt in ("-o", "--odir"):
            outputDir = arg
    
    firstFile = True
    
    # call the funcs to process the CSV file and fill the output file
    for item in tissues:
        parseCSVFile(item, inputDir, outputDir, 'egenes', firstFile)
        parseCSVFile(item, inputDir, outputDir, 'signif_variant_gene_pairs', firstFile)
        firstFile = False

####
# parses the individual tissue file
####
def parseCSVFile(tissue, inputDir, outputDir, fileType, firstFileFlag):

    try:
        # split the tissue declaration into its parts
        tissue_data = tissue.split(',')
        
        # get the complete in and output file names
        infileName = "{0}/{1}.v7.{2}.csv".format(inputDir, tissue_data[0], fileType)
        outfileName = "{0}/{1}.csv".format(outputDir, fileType)
        
        print("Processing input file: {0}, Sending to output file: {1}\n".format(infileName, outfileName))
    
        # get the tissue name
        tissueName = tissue_data[0].replace('_', ' ')
        
        # get the uberon code
        tissueUberon = tissue_data[1]
                
        # get the output file handle
        outFH = open(outfileName, 'a+')
    
        # get the expected number of columns for error checking
        if fileType == 'egenes':   
            colCount = 35        
        else:
            colCount = 14
        
        # init a line counter for error checking
        lineCount = 1
        
        # get the input file handle, skip the header line and parse the rest
        with open(infileName, 'r') as inFH:
            # skip the first header line
            firstLine = next(inFH)
            
            # if this if the first time for the output write out the header
            if firstFileFlag == True:
                outFH.write("tissue_name,tissue_uberon,{0}".format(firstLine).replace('\t', ','))

            # for the rest of the lines in the file 
            for line in inFH:       
                # prepend the input line with the tissue name and uberon id
                newLine = "{0},{1},{2}".format(tissueName, tissueUberon, line).replace('\t', ',')
                
                # make check to insure we have the correct number of columns
                numOfCols = newLine.split(',')
                
                # check the column count
                if len(numOfCols) != colCount:
                    print("Error with column count. Got:{0}, expected {1} in {2} at position {3}".format(len(numOfCols), colCount, infileName, lineCount))
            
                # increment the line counter
                lineCount += 1
                        
                # write the new line to the output file
                outFH.write(newLine)
            
        # close the input and output files
        inFH.close()
        outFH.close()
    except Exception as e:
        print("Error: {0}".format(e.message))
    
####
# main entry point to the process
####
if __name__ == "__main__":
    processCSVFiles(sys.argv[1:])

