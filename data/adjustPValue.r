



args = commandArgs(trailingOnly=TRUE)


if (length(args)==4){
print('running..')
} else {
print('IT SHOULD BE RUN AS: Rscript script subsector_file_as_input_in_the _1st_script tagRatio.subsectors.txt genomeBinFiles.txt tagRatio.subsectors.padj.txt')
}

subs  <- read.table(args[1])  ## subsector_file
subsectorFile <- args[2] ## tagRatio.subsectors.txt 
sample.sub <- read.table(subsectorFile)
genomelist <- read.table(args[3])[,1] ## the file including the genome bin file names
out1 <-    args[4] ##'tagRatio.subsectors.padj.txt'

enum0 <- 10 ## 10 columns for [ cat_rank, rank_order, id, gene_name, chr, strand, start, end, np1d, nm1d ] in subsector_out files

for (i in 1:nrow(subs)){
enum <- enum0+i
sample.genome <- read.table(toString(genomelist[i]))[,4]

e1 <- sample.sub
s1 <- sample.genome

s.log2 <- log2(s1[is.finite(s1) & s1>0])
dns <- density(s.log2, na.rm=T)

X <- dns$x
Y <- dns$y
i.C1 <- 1
i.mean1 <- median(s.log2)
i.sigma1 <- sd(s.log2[abs(s.log2-i.mean1)<2])

df <- data.frame(X, Y)
fit <- nls(Y ~ (C1 * exp(-(X-mean1)**2/(2 * sigma1**2)) ), data=df, start=list(C1=i.C1, mean1=i.mean1, sigma1=i.sigma1), algorithm="port")

p1 <- 1-pnorm(log2(e1[,enum]), fit$m$getPars()[2], fit$m$getPars()[3])
fdr1 <- p.adjust(p1, method='BH')

i
if (i == 1){
M <- cbind(e1[,1:enum0],fdr1)
} else {
M <- cbind(M,fdr1)
}


}

write.table(M, file=out1, quote=F, row.names=F, col.names=F)


