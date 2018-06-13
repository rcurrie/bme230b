# score BME assignment using F1 score
# script takes two arguments, the first argument is the prediction file and the second is the actual file
# example:
# Rscript BME230_F1score.R davids_pancan_response.tsv tcga_mutation_test_labels.tsv
# outputs a file named with the <predictions input filename>_scored.tsv

# load input file
args = commandArgs(trailingOnly=TRUE)
predict_input_file<<-args[1]
actual_labels_file<<-args[2]

# load files
predicted_response<-read.csv(file=predict_input_file,sep="\t")
# colnames(predicted_response)<-c("TumorTypePrediction","TP53MutationPrediction","KRASMutationPrediction","BRAFMutationPrediction")
true_response<-read.csv(file=actual_labels_file,sep="\t")


# for testing
#predicted_response<-read.csv(file="davids_tissue_specific_response.tsv",sep="\t")
#colnames(predicted_response)<-c("TumorTypePrediction","TP53MutationPrediction","KRASMutationPrediction","BRAFMutationPrediction")
#true_response<-read.csv(file="tcga_mutation_test_labels.tsv",sep="\t")

# score tumor type
# for each tumor type calculate an F1 score
tissue_scores<-data.frame(matrix(ncol=2,nrow=0))
tissues<-unique(true_response$primary.disease.or.tissue)
tissues_predict<-unique(predicted_response$TumorTypePrediction)

running_precision<-c()
running_recall<-c()
for (tissue in tissues) {
  TP<-length(which(predicted_response$TumorTypePrediction == tissue & true_response$primary.disease.or.tissue == tissue))
  FP<-length(which(predicted_response$TumorTypePrediction == tissue & true_response$primary.disease.or.tissue != tissue))
  FN<-length(which(predicted_response$TumorTypePrediction != tissue & true_response$primary.disease.or.tissue == tissue))
  if ((TP+FP) > 0) { precision<-TP/(TP+FP) } else { precision<-0 }
  if ((TP+FN) > 0) { recall<-TP/(TP+FN) } else { recall <- 0 }
  running_precision<-c(running_precision,precision)
  running_recall<-c(running_recall,recall)
  if ((precision*recall)!=0) 
    { tissue_specific_F1_score<-(2*precision*recall)/(precision+recall) }
  else 
    {tissue_specific_F1_score<-0}
  tissue_scores<-rbind(tissue_scores,cbind(paste0(tissue,"_F1_score"),"V2"=tissue_specific_F1_score))
  print(paste0(tissue,"_F1_score: ",tissue_specific_F1_score))
  }

# take mean of precision and recall
tissue_precision<-sum(running_precision)/length(tissues)
tissue_recall<-sum(running_recall)/length(tissues)
tissue_F1_score<-(2*tissue_precision*tissue_recall)/(tissue_precision+tissue_recall)
print(paste("Overall Tissue F1 score:",tissue_F1_score))

  # score TP53 mutation predictions
TP<-length(which(predicted_response$TP53MutationPrediction ==1 & true_response$TP53_mutant==1))
FP<-length(which(predicted_response$TP53MutationPrediction ==1 & true_response$TP53_mutant==0))
FN<-length(which(predicted_response$TP53MutationPrediction ==0 & true_response$TP53_mutant==1))
if ((TP+FP) > 0) { TP53_precision<-TP/(TP+FP) } else { TP53_precision<-0 }
if ((TP+FN) > 0) { TP53_recall<-TP/(TP+FN) } else { TP53_recall <- 0 }
TP53_F1_score<-(2*TP53_precision*TP53_recall)/(TP53_precision+TP53_recall)
print(paste("TP53_F1_score:",TP53_F1_score))


# score KRAS mutation predictions
TP<-length(which(predicted_response$KRASMutationPrediction ==1 & true_response$KRAS_mutant==1))
FP<-length(which(predicted_response$KRASMutationPrediction ==1 & true_response$KRAS_mutant==0))
FN<-length(which(predicted_response$KRASMutationPrediction ==0 & true_response$KRAS_mutant==1))
if ((TP+FP) > 0) { KRAS_precision<-TP/(TP+FP) } else { KRAS_precision<-0 }
if ((TP+FN) > 0) { KRAS_recall<-TP/(TP+FN) } else { KRAS_recall <- 0 }
KRAS_F1_score<-(2*KRAS_precision*KRAS_recall)/(KRAS_precision+KRAS_recall)
print(paste("KRAS_F1_score:",KRAS_F1_score))


# score BRAF mutation predictions
TP<-length(which(predicted_response$BRAFMutationPrediction ==1 & true_response$BRAF_mutant==1))
FP<-length(which(predicted_response$BRAFMutationPrediction ==1 & true_response$BRAF_mutant==0))
FN<-length(which(predicted_response$BRAFMutationPrediction ==0 & true_response$BRAF_mutant==1))
if ((TP+FP) > 0) { BRAF_precision<-TP/(TP+FP) } else { BRAF_precision<-0 }
if ((TP+FN) > 0) { BRAF_recall<-TP/(TP+FN) } else { BRAF_recall <- 0 }
BRAF_F1_score<-(2*BRAF_precision*BRAF_recall)/(BRAF_precision+BRAF_recall)
print(paste("BRAF_F1_score:",BRAF_F1_score))



mutation_precision<-(TP53_precision+KRAS_precision+BRAF_precision)/3
mutation_recall<-(TP53_recall+KRAS_recall+BRAF_recall)/3
mutation_F1_score<-(2*mutation_precision*mutation_recall)/(mutation_precision+mutation_recall)
print(paste("Mutation_F1_score:",mutation_F1_score))



final_precision<-(mutation_precision+tissue_precision)/2
final_recall<-(mutation_recall+tissue_recall)/2
final_F1_score<-(2*final_precision*final_recall)/(final_precision+final_recall)
print(paste("Final_F1_score:",final_F1_score))


other_scores<-rbind(c("Tumor_Type_F1_score",tissue_F1_score),
                    c("TP53_F1_score",TP53_F1_score),
                    c("KRAS_F1_score",KRAS_F1_score),
                    c("BRAF_F1_score",BRAF_F1_score),
                    c("Mutation_F1_score",mutation_F1_score),
                    c("Final_F1_score",final_F1_score))
score_vector<-rbind(tissue_scores,other_scores)

output_filename<-paste0(strsplit(predict_input_file,"\\.")[[1]][1],"_scored.tsv")

# write.table((score_vector),quote=FALSE,file=output_filename,sep="\t",col.names = FALSE,row.names = FALSE)

