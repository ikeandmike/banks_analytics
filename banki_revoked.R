library(rvest)
library(XML)
library(RCurl)
library(progress)

# banki does not have a friendly export feature for its collection
# of revoked banks. It comes in 50 webpages, so we'll go through each
# webpage, download the html table, combine it into one dataframe,
# and save as csv.
final_set <- NULL

# Fancy progress bar.
#pb <- progress_bar$new(
#  format = paste0("[:bar] :percent"),
#  total = 60, clear = FALSE)

# There's no way to know how webpages there will be,
# especially because when I tested an out-of-bounds page number,
# it circled back to one. :/
# So instead, on the first duplicate we'll stop.

content <- html_table(read_html("http://www.banki.ru/banks/memory/?PAGEN_1=1"))
# First row of data minus the id column.
# We'll use the whole goddamn thing to grepl.
first <- content[[3]][1,2:ncol(content[[3]])]

cat("Downloading... [")

i <- 1
repeat {

  # Construct the URL.
  url <- paste0("http://www.banki.ru/banks/memory/?PAGEN_1=",i)
  
  # Read the html table. It returns a list, where the 3rd element is our table.
  content <- html_table(read_html(url))
  
  df = content[[3]]
  
  # Collect to single dataframe.
  final_set <- rbind(final_set, df)
  
  test <- final_set %>%
    select(-` `)
  
  if(any(duplicated(test) | duplicated(test, fromLast = T))) break
  
  i <- i + 1
  cat("=")
  
}

cat("]\n")

# Cleanup column names.
names(final_set) <- c("id","bank", "lic.num", "cause","review.date","region")

final_set <- final_set %>%
  select(-id) %>%
  distinct()

# Tranlsate the "cause" column.
final_set$cause <- gsub(pattern = "отозв.", replacement = "Revoked",
                            final_set$cause)

final_set$cause <- gsub(pattern = "ликв.", replacement = "Liq",
                           final_set$cause)

# Save to csv.
write.csv(final_set, file.path(getwd(),"banki_revoked.csv"))
write.csv(final_set, file.path(
  "/Users/jabortell/Google Drive/Deloitte-IQP/Data Files/banki",
  "banki_revoked.csv"))
