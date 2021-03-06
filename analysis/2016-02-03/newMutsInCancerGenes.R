##compare cancer genes for mutational data.


source("../../bin/WGSData.R")

##now store the file
#cfile='../../data/Census_allTue Jan 19 18-58-56 2016.csv'
#synStore(File(cfile,parentId='syn4984723'))

require(parallel)
##now get
cancer.genes=read.table(synGet('syn5610781')@filePath,sep=',',header=T)

impact=c("LOW",'MODERATE','HIGH')
  allsoms<-synapseQuery("select * from entity where parentId=='syn5578958'")
  print(paste('Selecting from',nrow(allsoms),'mutation files'))
  allsoms=allsoms[unlist(sapply(impact,grep,allsoms$entity.name)),]
  print(paste("Found",nrow(allsoms),'with',paste(impact,collapse=' or '),'impact'))
  som.germ=getAllMutData(allsoms)

allstats<-mclapply(as.character(cancer.genes[,1]),function(x) try(getMutationStatsForGene(gene=x,doPlot=FALSE,som.germ=som.germ)),mc.cores=24)

names(allstats)<-as.character(cancer.genes[,1])

fulldf<-data.frame(Hugo_Symbol=unlist(sapply(allstats,function(x) as.character(x$Hugo_Symbol))),
                   Protein_Change=unlist(sapply(allstats,function(x) as.character(x$Protein_Change))),
                   Sample_ID=unlist(sapply(allstats,function(x) as.character(x$Sample_ID))),
                   Mutation_Status=unlist(sapply(allstats,function(x) as.character(x$Mutation_Status))),
                   Chromosome = unlist(sapply(allstats,function(x) as.character(x$Chromosome))),
                   Start_Position = unlist(sapply(allstats,function(x) as.character(x$Start_Position))),
                   End_Position = unlist(sapply(allstats,function(x) as.character(x$End_Position))),
                   Reference_Allele = unlist(sapply(allstats,function(x) as.character(x$Reference_Allele))),
                   Variant_Allele = unlist(sapply(allstats,function(x) as.character(x$Variant_Allele))),
                   Mutation_Type = unlist(sapply(allstats,function(x) as.character( x$Mutation_Type))))

udf<-unique(fulldf)

write.table(udf,file='allCancerGeneMutationsInDermals.tsv',sep='\t',row.names=F,quote=F)
write.table(subset(udf,Mutation_Status=="Germline"),file='germlineCancerGeneMutationsInDermals.tsv',sep='\t',row.names=F,quote=F)
write.table(subset(udf,Mutation_Status=="Somatic"),file='somaticCancerGeneMutationsInDermals.tsv',sep='\t',row.names=F,quote=F)

for(f in c("allCancerGeneMutationsInDermals.tsv","germlineCancerGeneMutationsInDermals.tsv","somaticCancerGeneMutationsInDermals.tsv"))
    synStore(File(f,parentId='syn5605256'),executed=list(list(url='https://raw.githubusercontent.com/Sage-Bionetworks/dermalNF/master/analysis/2016-01-27/mutsInCancerGenes.R')),used=list(list(entity='syn5610781')))
