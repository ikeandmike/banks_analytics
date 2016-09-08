
# Download from banki
cat("Collecting data from banki.ru\n")
s_collector <- file.path(getwd(), "scripts", "banki_collector.R")
source(s_collector)

# Merge banki and CBR and caculate months until revocation
cat("\nMerging banki and CBR. Calculating months until revocation.\n")
s_months <- file.path(getwd(), "scripts", "banki_months.R")
source(s_months)

# Also download banki's revocation dataset.
cat("\nUpdating extra revocation dataset.\n")
s_revoked <- file.path(getwd(), "scripts", "banki_revoked.R")
source(s_revoked)

# Clean Global Environment
rm(list = ls())

cat("\nProcess complete.\n")