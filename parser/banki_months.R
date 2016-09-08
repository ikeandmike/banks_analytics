library(dplyr)
library(tidyr)
library(lubridate)
library(progress)

# For now, we're only gather N1, N2, and N3. If we add indicators,
# then this process will become generalized.
n1 <- read.csv( file.path(getwd(), "exports", "performance","1600.csv") )
n2 <- read.csv( file.path(getwd(), "exports", "performance","1700.csv") )
n3 <- read.csv( file.path(getwd(), "exports", "performance","1800.csv") )

# Combine to one dataframe.
n123 <- rbind(n1, n2, n3)

# Clean library.
remove(n1, n2, n3)

# The dataframe is in long format, meaning the indicators are in one column.
# We'll spread the indicators into their own columns.
n123 <- n123 %>%
  select(lic.num, ind, ind.end, time.end) %>%
  spread(ind, ind.end) %>%
  arrange(time.end, lic.num)

# Clean the column names.
names(n123) <- c("lic.num", "time.end", "N1", "N2", "N3")

# Convert character date column to actual date format.
n123$time.end <- ymd(n123$time.end)

# I know, lots of repeated code. I'll make it generalized later.
# Right now, it converts the European comma-decimal to point-decimal,
# removes the spacing for thousounds and so on, and converts it to numeric.
n123$N1 <- gsub(pattern = " ", replacement = "", n123$N1)
n123$N1 <- sub(pattern = ",", replacement = ".", n123$N1)
n123$N1 <- as.numeric(n123$N1) # Matches CBR dataset

n123$N2 <- gsub(pattern = " ", replacement = "", n123$N2)
n123$N2 <- sub(pattern = ",", replacement = ".", n123$N2)
n123$N2 <- as.numeric(n123$N2)/100 # banki represented the data as percentages.

n123$N3 <- gsub(pattern = " ", replacement = "", n123$N3)
n123$N3 <- sub(pattern = ",", replacement = ".", n123$N3)
n123$N3 <- as.numeric(n123$N3)/100 # same thing

## Cleanup CBR ####

# Adds our CBR dataset to environment.
cbr <- read.csv(
  file.path(getwd(), "banks_standards(summer file).csv")
)

# Makes date format.
cbr$Period <- dmy(cbr$Period)

# Cleanup banki_revoked ####

# Loads revocations dataset.
banki_revoked <- read.csv(
  file.path(getwd(), "banki_revoked.csv")
)

# Actual date format.
banki_revoked$review.date <- dmy(banki_revoked$review.date)

## COMBINE DATA ####

# Joins CBR and banki into one dataframe.
# Has banki's N1, N2, and N3, and CBR N1, N2, and N3.
cbr_banki <- n123 %>%
  full_join(y = cbr, by = c("lic.num" = "Lic_num", "time.end" = "Period"))



# Banki has many NA data points, so...
# If banki is missing, and there is a CBR datapoint which is not 0
# (we're not too sure about the 0 values), then we'll copy the CBR N1, etc.
# to the banki N1.

# x is banki
# y is cbr
x <- 3 #n1.x
y <- 7 #n1.y

# To copy the data like I mentioned.
for (j in 1:3) {
  
  # Fancy progress bar.
  pb <- progress_bar$new(
    format = paste0("N",j," [:bar] :percent eta: :eta"),
    total = nrow(cbr_banki), clear = FALSE, width= 80)

  for (i in 1:nrow(cbr_banki)) {
    n.x <- cbr_banki[i, x]
    n.y <- cbr_banki[i, y]
    
    # if N_.x (banki's N1) is empty and N_.y is not empty or 0,
    # then copy N_.y to N_.x
    if ( is.na(n.x) & !is.na(n.y) ) {
      if (n.y != 0) cbr_banki[i, x] <- n.y
    }
    
    cat("\rRow:",i)
    # Moves progress bar.
    #pb$tick()
  }
  # Moves from banki and CBR N1 to banki and CBR N2, etc.
  x <- x+1
  y <- y+1
}

# Remove CBR's N1, N2, and N3.
cbr_banki_merged <- cbr_banki %>%
  select(-N1.y, -N2.y, -N3.y)

# Cleanup the names.
names(cbr_banki_merged) <-
  c("lic.num", "time.end", "N1", "N2", "N3", "Status",
    "N4", "N7", "N9_1", "N10_1", "N12")

# Now we must figure out the number of months until a bank's license
# was revoked. We'll just take the min and max dates for a revoked bank,
# subtract them, and add them back to the dataset.
revocations <- cbr_banki_merged %>%
  filter(Status == "Revoked") %>%
  group_by(lic.num) %>%
  summarise(start = min(time.end), revoked = max(time.end))

# Convert to POSIXlt so we can math the dates.
revocations$start <- as.POSIXlt(revocations$start)
revocations$revoked <- as.POSIXlt(revocations$revoked)

# The number of months between dates is the number of years times months,
# plus the months in between the final year.
revocations$months <- 12 *
  (revocations$revoked$year - revocations$start$year) +
  (revocations$revoked$mon - revocations$start$mon)

# We'll remove the date fields.
revocations_months <- revocations %>% select(-start, -revoked)

# Add the months back to the dataset.
final_set <- cbr_banki_merged %>%
  left_join(y = revocations_months, by = c("lic.num", "lic.num"))

# Save to csv in working directory.
write.csv(final_set, file.path(getwd(),
                               paste0("banki_cbr_final_",today(),".csv")))

# Save to Google Drive
write.csv(final_set,
          file.path(
            "/Users/jabortell/Google Drive/Deloitte-IQP/Data Files/banki",
                               paste0("banki_cbr_final_", today(),".csv")
            )
          )
