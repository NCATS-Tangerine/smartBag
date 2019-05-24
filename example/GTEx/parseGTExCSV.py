import sys, getopt, csv

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
"Brain_Cortex,0001851",
"Brain_Frontal_Cortex_BA9,0013540",
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

reference_chrom_labels = {
    'b37': {
        'p1': {
            1: 'NC_000001.10', 2: 'NC_000002.11', 3: 'NC_000003.11', 4: 'NC_000004.11', 5: 'NC_000005.9',
            6: 'NC_000006.11', 7: 'NC_000007.13', 8: 'NC_000008.10', 9: 'NC_000009.11', 10: 'NC_000010.10', 11: 'NC_000011.9',
            12: 'NC_000012.11', 13: 'NC_000013.10', 14: 'NC_000014.8', 15: 'NC_000015.9', 16: 'NC_000016.9', 17: 'NC_000017.10',
            18: 'NC_000018.9', 19: 'NC_000019.9', 20: 'NC_000020.10', 21: 'NC_000021.8', 22: 'NC_000022.10', 23: 'NC_000023.10',
            24: 'NC_000024.9'
        }
    },
    'b38': {
        'p1': {
            1: 'NC_000001.11', 2: 'NC_000002.12', 3: 'NC_000003.12', 4: 'NC_000004.12', 5: 'NC_000005.10',
            6: 'NC_000006.12', 7: 'NC_000007.14', 8: 'NC_000008.11', 9: 'NC_000009.12', 10: 'NC_000010.11', 11: 'NC_000011.10',
            12: 'NC_000012.12', 13: 'NC_000013.11', 14: 'NC_000014.9', 15: 'NC_000015.10', 16: 'NC_000016.10', 17: 'NC_000017.11',
            18: 'NC_000018.10', 19: 'NC_000019.10', 20: 'NC_000020.11', 21: 'NC_000021.9', 22: 'NC_000022.11', 23: 'NC_000023.11',
            24: 'NC_000024.10'
        }
    }
}


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
        parseCSVFile(item, inputDir, outputDir, 'egenes', 11, firstFile)
        parseCSVFile(item, inputDir, outputDir, 'signif_variant_gene_pairs', 0, firstFile)
        firstFile = False

####
# parses the individual tissue file
####
def parseCSVFile(tissue, inputDir, outputDir, fileType, variant_id_index, firstFileFlag):

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
            colCount = 36
        else:
            colCount = 15
        
        # init a line counter for error checking
        lineCount = 1
        
        # get the input file handle, skip the header line and parse the rest
        with open(infileName, 'r') as inFH:
            # skip the first header line
            firstLine = next(inFH)
            
            # if this if the first time for the output write out the header
            if firstFileFlag == True:
                outFH.write("tissue_name,tissue_uberon,HGVS,{0}".format(firstLine).replace('\t', ','))

            # for the rest of the lines in the file 
            for line in inFH:
                # split the into an array
                newLine = line.split('\t')

                # get the variant ID value
                variant_id = newLine[variant_id_index]

                # get the HGVS value
                HGVS = get_HGVS_value(variant_id)

                # prepend the input line with the tissue name and uberon id
                newLine = "{0},{1},{2},{3}".format(tissueName, tissueUberon, HGVS, line).replace('\t', ',')
                
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
# parses the GTEx variant ID and converts it to an HGVS expression
####
def get_HGVS_value(gtex_variant_id):
    try:
        # split the string into the components
        variant_id = gtex_variant_id.split('_')

        # get position indexes into the data element
        reference_patch = 'p1'
        position = int(variant_id[1])
        ref_allele = variant_id[2]
        alt_allele = variant_id[3]
        reference_genome = variant_id[4]
        chromosome = variant_id[0]

        # X or Y to integer values for proper indexing
        if chromosome == 'X':
            chromosome = 23
        elif chromosome == 'Y':
            chromosome = 24
        else:
            chromosome = int(variant_id[0])

        # get the HGVS chromosome label
        ref_chromosome = reference_chrom_labels[reference_genome][reference_patch][chromosome]
    except KeyError:
        return ''

    # get the length of the reference allele
    len_ref = len(ref_allele)

    # is there an alt allele
    if alt_allele == '.':
        # deletions
        if len_ref == 1:
            variation = f'{position}del'
        else:
            variation = f'{position}_{position + len_ref - 1}del'

    elif alt_allele.startswith('<'):
        # we know about these but don't support them yet
        return ''

    else:
        # get the length of the alternate allele
        len_alt = len(alt_allele)

        # if this is a SNP
        if (len_ref == 1) and (len_alt == 1):
            # simple layout of ref/alt SNP
            variation = f'{position}{ref_allele}>{alt_allele}'
        # if the alternate allele is larger than the reference is an insert
        elif (len_alt > len_ref) and alt_allele.startswith(ref_allele):
            # get the length of the insertion
            diff = len_alt - len_ref

            # get the position offset
            offset = len_alt - diff

            # layout the insert
            variation = f'{position + offset - 1}_{position + offset}ins{alt_allele[offset:]}'
        # if the reference is larger than the deletion it is a deletion
        elif (len_ref > len_alt) and ref_allele.startswith(alt_allele):
            # get the length of the deletion
            diff = len_ref - len_alt

            # get the position offset
            offset = len_ref - diff

            # if the diff is only 1 BP
            if diff == 1:
                # layout the SNP deletion
                variation = f'{position + offset}del'
            # else this is more that a single BP deletion
            else:
                # layout the deletion
                variation = f'{position + offset}_{position + offset + diff - 1}del'
        # we do not support this allele
        else:
           return ''

    # layout the final HGVS expression in curie format
    hgvs: str = f'{ref_chromosome}:g.{variation}'

    # convert the reference genome to a project standard. danger, hack job ahead.
    if reference_genome == 'b37':
        reference_genome = 'HG19'
    else:
        reference_genome = 'HG38'

    # return the expression to the caller
    return hgvs

####
# main entry point to the process
####
if __name__ == "__main__":
    processCSVFiles(sys.argv[1:])

