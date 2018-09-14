## Description

This data represents gene to column enrichment associations, for genes and columns belonging to each 
bicluster found in the RNAseqDB data by the Massive Associative K-biclustering (MAK) algorithm.


### Column definitions:

**bicluster** - index of the bicluster, sorted decreasing by score.  
**gene** - NCBI gene identifier.  
**bicluster_score** - the score of the bicluster.  
**bicluster_mean** - the mean value of the bicluster data.  
**gene_bicluster_cor** - mean pairwise row correlation between this gene and all other genes in the bicluster, restricted to the bicluster data.  
**col_enrich_all** - all ids for enriched column terms.  
**col_enrich_MONDO** - MONDO ids for enriched column terms.  
**col_enrich_MONDO_label** - labels for enriched column terms.  
**col_enrich_UBERON** - UBERON ids for enriched column terms.  
**col_enrich_UBERON_label** - labels for enriched column terms.  
**col_enrich_DOID** - DOID ids for enriched column terms.  
**col_enrich_DOID_label** - labels for enriched column terms.  
**col_enrich_NCIT** - NCIT ids for enriched column terms.  
**col_enrich_NCIT_label** - labels for enriched column terms.  
**all_col_labels** - labels for all column terms.
