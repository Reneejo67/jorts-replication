library(data.table)
library(did2s)
library(HonestDiD)
library(ggplot2)
add_el <- theme_grey() + theme(text = element_text(family = "Times", size=20))
theme_set(add_el)
getAnywhere(honest_did_did2s)

# pulling in data and specifying types
cls = c(id="factor", X='vector', G2='numeric', G='factor',  Y='numeric', period= 'numeric', treat= 'numeric', ts='numeric')
data = read.table('~/jorts_replication/data/all_jkr_did_data_test_all_new_denom.tsv',  stringsAsFactors = FALSE, sep = '\t', header = TRUE, colClasses=cls)

# constructing matrix for Di2S
mtx = matrix(, nrow=dim(data)[1], ncol=16)
for (r in 1:dim(data)[1]) {
  vect = data$X[r]
  vect = strsplit(vect, ',')
  vect = as.numeric(unlist(vect))
  mtx[r,] = vect
}

data['X'] = mtx
data = as.data.table(data)

# running DiD2S on non-IA non-TERF accounts
g0 = data[data$G == 0]
static0 = did2s(g0, 
                yname = "Y", first_stage = ~ 0 | id + period,
                second_stage = ~i(ts), treatment = "treat",
                cluster_var = "id")
fixest::esttable(static0)

# sensitivity analysis
sensitivity_results0 <- static0 |>
  get_honestdid_obj_did2s(coef_name = "ts") |>
  honest_did_did2s(
    e = 0,
    type = "relative_magnitude",
    Mbarvec = seq(from = 0.5, to = 4, by = 0.5)
  )
sensitivity_results0
plot0 <- HonestDiD::createSensitivityPlot_relativeMagnitudes(
  sensitivity_results0$robust_ci,
  sensitivity_results0$orig_ci,
)
theme_update(base_size=20)
plot(plot0)

# running DiD2S on IA non-TERF accounts
g1 = data[data$G == 1]
static1 = did2s(g1, 
                yname = "Y", first_stage = ~ 0 | id + period,
                second_stage = ~i(ts), treatment = "treat",
                cluster_var = "id")
fixest::esttable(static1)

# sensitivity analysis
sensitivity_results1 <- static1 |>
  get_honestdid_obj_did2s(coef_name = "ts") |>
  honest_did_did2s(
    e = 0,
    type = "relative_magnitude",
    Mbarvec = seq(from = 0.5, to = 4, by = 0.5)
  )
sensitivity_results1
HonestDiD::createSensitivityPlot_relativeMagnitudes(
  sensitivity_results1$robust_ci,
  sensitivity_results1$orig_ci,

)

# running DiD2S on non-IA TERF accounts
g2 = data[data$G == 2]
static2 = did2s(g2, 
                yname = "Y", first_stage = ~ 0 | id + period,
                second_stage = ~i(ts), treatment = "treat",
                cluster_var = "id")
fixest::esttable(static2)

# sensitivity analysis
sensitivity_results2 <- static2 |>
  get_honestdid_obj_did2s(coef_name = "ts") |>
  honest_did_did2s(
    e = 0,
    type = "relative_magnitude",
    Mbarvec = seq(from = 0.5, to = 4, by = 0.5)
  )
sensitivity_results2
HonestDiD::createSensitivityPlot_relativeMagnitudes(
  sensitivity_results2$robust_ci,
  sensitivity_results2$orig_ci,
)

# running DiD2S on IA TERF accounts
g3 = data[data$G == 3]
static3 = did2s(g3, 
                yname = "Y", first_stage = ~ 0 | id + period,
                second_stage = ~i(ts), treatment = "treat",
                cluster_var = "id")
fixest::esttable(static3)

# sensitivity analysis
sensitivity_results3 <- static3 |>
  get_honestdid_obj_did2s(coef_name = "ts") |>
  honest_did_did2s(
    e = 0,
    type = "relative_magnitude",
    Mbarvec = seq(from = 0.5, to = 4, by = 0.5)
  )
sensitivity_results3
HonestDiD::createSensitivityPlot_relativeMagnitudes(
  sensitivity_results3$robust_ci,
  sensitivity_results3$orig_ci,
)

# Full plot
fixest::iplot(
  list(static0, static1, static2, static3), 
  main="Effect of treatment on following rate change",
  xlab="Relative time to RT",
  col=c("steelblue", "green", "red", "purple"),
  )

legend(x=-15, y=-0.000005, col = c("steelblue", "green", "red", "purple"), pch = c(20, 18), 
       legend=c("non-TERF non-IA", "non-TERF IA", "TERF non-IA", "TERF IA"))
