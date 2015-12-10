'''
This is the primary script that can be used to process the VCFs after GTK is run
on them. It requires an installation of vcf2maf.pl and VEP.
'''

##VCF2MAF installation:
vcf2maf='perl ../../../vcf2maf-master/vcf2maf.pl'
##REFERENCE FASTA installation
reffasta='../../lib/ucsc.hg19.fasta'
##OUTPUT FROM GATK:



import synapseclient,re,os
syn = synapseclient.Synapse()
syn.login()

vcf_file=syn.get('syn5526663').path


##get all the VCF annotations so that we can process the merged file
wgs_vcf='syn5522788'
#get all files
query_res=syn.query("select id, name from entity where entity.parentId=='"+wgs_vcf+"'")
##now get metadata for all files
syn_files=dict([(res['entity.id'],res['entity.name']) for res in query_res['results'] if 'hard-filtered' not in res['entity.name']])
syn_ids=syn_files.keys()

##now get metadata only for these files to determine which synapse ids belong to
##a specific patient
annotes=[syn.getAnnotations(a) for a in syn_ids]

for pat in ['1','2','3','4','5','6','7','8','9','10','11','12','13']:

    #now for each patient, determine which samples are in blood vs. tumor
    p1ids=[a for a in annotes if a['patientID'][0] in ['CT00000'+pat,'CT0000'+pat]]
    blood=[a['id'] for a in p1ids if a['tissueID'][0]=='PBMC']
    tumor=[a['id'] for a in p1ids if a['tissueID'][0]!='PBMC']

    print 'Found %d tumor samples and %d blood samples for patient %s'%(len(tumor),len(blood),pat)

    if len(blood)>0 and blood[0] in syn_files.keys():
        bloodfile=re.sub('.vcf','',syn_files[blood[0]])
    else:
        bloodfile=''


    for t in tumor:
        tumfile=re.sub('.vcf','',syn_files[t])
        tumfile_annotations=syn.get(t,downloadFile=False).annotations
        if(bloodfile==''):
            print "Missing normal for patient %s, running without"%(pat)
            sstring=tumfile
        else:
            print t,blood[0]
            sstring=','.join([tumfile,bloodfile])
        cmfile='patient_'+pat+'_'+tumfile+'_'+bloodfile+'_commands.sh'
        patsh=open(cmfile,'w')
        ##first create vcf file with only two samples
        bcftoolscmd="bcftools view %s -s %s -U"%(vcf_file,sstring)
        if(bloodfile==''):
            outvcf="patient%s_tumor_%s_only.vcf"%(pat,t)
            outmaf="tumorVsNormal_pat%s_tumor_%s_only.maf"%(pat,t)
        else:
            outvcf="patient%s_tumor_%s_vs_norm_%s.vcf"%(pat,t,blood[0])
            outmaf="tumorVsNormal_pat%s_tumor_%s_vs_norm_%s.maf"%(pat,t,blood[0])
        patsh.write(bcftoolscmd+'>'+outvcf+'\nbgzip '+outvcf+'\n')
        #then run vcf2maf on that subset

                #create new annotation string
        #activity string?
        annotationstr="'{\"dataType\":\"WGS\",\"tissueType\":\"tumorVsNormal\",\"patientId\":\""+tumfile_annotations['patientID'][0]+"\""
        annotationstr=annotationstr+",\"tissueID\":\""+tumfile_annotations['tissueID'][0]+"\"}'"

#	if bloodfile=='':
#	    usedstr="'{"+t+"}'"
#	else:
#	    usedstr="'{"+t+","+blood[0]+"}'"

        ##now store paired VCF
        synapse_upload_vcf="synapse store "+outvcf+".gz --parentId=syn5522791 --annotations "+annotationstr#+' --used '+usedstr

        patsh.write(synapse_upload_vcf+'\n\n')

	patsh.write('bgzip -d '+outvcf+'.gz\n\n')
        vcf2maf_cmd=vcf2maf+" --input-vcf %s --vcf-tumor-id %s --vcf-normal-id %s --output-maf %s \
         --vep-forks 16 --species homo_sapiens --ref-fasta %s"%(outvcf,tumfile,bloodfile,outmaf,reffasta)

        patsh.write(vcf2maf_cmd+'\n\n')
        #then these file should be uploaded to synapse

        synapse_upload_maf="synapse store "+outmaf+" --parentId=syn5522808 --annotations "+annotationstr#+' --used '+usedstr
        patsh.write(synapse_upload_maf+'\n')

        #patsh.write(bcftoolscmd+'>'+outvcf+'\n'+vcf2maf_cmd+'\n')
        #os.system(cmd)
        patsh.close()
    #os.system('sh '+cmfile+' &')

        #examples for patient 1
'''
syn4987466 syn4985519
syn4985596 syn4985519
syn4985378 syn4985519
##here is the test command, as far as I can tell...
perl ../../../vcf2maf-master/vcf2maf.pl --input-vcf recalibrated_indels_for_recalibrated_snps_for_dermalNFall.vcf --tumor-id=syn4987466 --normal-id=syn4985519 --output-maf=tumorVsNormal_pat1.maf
'''
