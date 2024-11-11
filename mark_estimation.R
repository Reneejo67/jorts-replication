library("RMark")
dset = import.chdata('jkr_indiv_non_foll.txt', header=FALSE , field.names=c("ch"))
mod = mark(dset, model="POPAN")
print(mod$results$derived)
