library(RCurl)
library(dplyr)
library(lubridate)
library(progress)

# indicators.csv contains banki.ru's ID codes for their indicators.
# i.e. N1 (Captial Adequacy Ratio) is 1600.
# The csv also has the names for the codes and banki's categorization.
indicators <- read.csv(file.path(getwd(),"indicators.csv"))

# banki has three types of indicators: Basic, Performance, and Carrying Amounts.
# N1, N2, and N3 are Performance Indicators, so we might as well download
# all of them.
type_filter <- "Performance Indicators"

# Filter out the data according to type_filter defined above.
indicators <- indicators %>%
  filter(type == type_filter) %>%
  select(code, indicator)

# Define a vector of the codes.
indicator_IDs <- indicators$code

# Throughout the download process, we should keep track of download failures,
# as well as wonky rows with NA licenses. We can then include it in a
# well-rounded methodology and results.
process_report <-
  data.frame(ind = character(0),
             download.failures = numeric(0),
             lic.na = numeric(0))

# banki.ru holds their data by month, year, and indicator,
# so we'll iterate through every date combination.
months <- c(1,2,3,4,5,6,7,8,9,10,11,12)
years <- c(2008,2009,2010,2011,2012,2013,2014,2015,2016)


# Here we begin our iteration. For every indicator, we'll download
# for every year, every month. And there's a fancy progress bar.
for (k in indicator_IDs) {
  
  # Fancy progress bar for each set of downloads per k-indicator.
  pb <- progress_bar$new(
    format = paste0("Ind: ",k," [:bar] :percent eta: :eta"),
    total = length(years) * length(months), clear = FALSE, width= 80)
  
  # The final_set will be all the data for an indicator and saved as a csv.
  # However, we can only download single months at a time, so we'll rbind
  # each month into final_set.
  final_set <- NULL
  
  # Turns out there are some failed downloads. We'll keep track for each
  # indicator in our process_report and save as csv later.
  download_misses <<- 0
  
  # We'll download for every year, every month for indicator k.
  for (i in years) {
    for (j in months) {
      
      # Moves the progress bar.
      pb$tick()
      
      # Recall that banki.ru's data is held in months, and it reports
      # a bank's state at the end of a month. On the website,
      # we must select the starting and ending months.
      
      end_month <- j + 1 # Remember that j is the iterating month.
      
      end_year <- i      # Remember that i is the iterating year.
                         # The only case when end_year does not
                         # equal i will be when the months are
                         # between December and January.
      
      if (j == 12) {      # If the starting month is December,
        end_month <- 1    # change the ending month to Janurary, and
        end_year <- i + 1 # jump to next year.
      }
      
      # Our ending and starting dates in actual date format.
      time.end <- ymd(paste(end_year,end_month,"01",sep="-"))
      time.start <- ymd(paste(i,j,"01",sep="-"))
      
      # Constructs the url which requests the download.
      url <- paste0(
        "http://www.banki.ru/banks/ratings/export.php?LANG=en&",
        "PROPERTY_ID=",k, # Recall that k is the indicator
        "&search[type]=name&sort_param=rating&sort_order=ASC&REGION_ID=0&",
        "date1=", time.end,   # date1 is the ending date
        "&date2=", time.start, # date2 is the starting date
        "&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0")
      
      # Read the url into a csv file.
      # If there is no data, then bank_data will be a 0-row dataframe.
      # If there is a download error, such as invalid byte-string crap, then
      # bank_data becomes NULL. We skip rbinding and continue to next month.
      bank_data <- tryCatch(
        {
        read.csv2(url, skip = 3, stringsAsFactors = F)
          },
        error=function(cond) {
          download_misses <<- download_misses + 1
          return(NULL)
        }
      )
      
      # If there was a download error, bank_data is null, then move on.
      if (is.null(bank_data)) next
      
      # if there is no data for this period or indicator, then move on.
      # (No error, just saves time.)
      if (nrow(bank_data) == 0) next
      
      # For some reason, the column names are usually misaligned.
      # And sometimes column names are different between types of indicators,
      # such as "Basic Indicators" and "Performance Inidicators".
      # If you try downloading Basic Indicators, there could be a problem,
      # so watch out.
      #
      # Also, notice that final column I named "empty". No idea why, but the
      # data just comes with a hanging empty column filled with NAs.
      names(bank_data) <-
        c("rating.change","bank.name","lic.num",
          "region","ind.end","ind.start","perc.change","empty")
      
      # Remove extraneous column which I renamed "empty".
        bank_data <- bank_data %>%
          select(-empty)
      
      # We'll add some new columns to...
      bank_data$rating <- 1:nrow(bank_data) # ..remember the rating
      bank_data$ind <- k                    # ..remember the indicator
      bank_data$time.start <- time.start    # ..remember the start date
      bank_data$time.end <- time.end        # ..remember the end date
      
      
      # Finally, we'll collect the month's data into a final dataframe.
      # When we've iterated through all the months and years for an
      # indicator-k, final_set will be written to csv and erased again up top.
      final_set <- rbind(final_set, bank_data)
      
    } # End j (month)
    
  } # End i (year)
  
  # Remember I want to keep track of wonky license NAs, so we'll count the
  # rows before and after I remove them.
  before_clean <- nrow(final_set)
  
  # Remove rows with NA licenses.
  final_set <- final_set %>%
    filter(!is.na(lic.num))
  
  after_clean <- nrow(final_set)
  
  # process_report will contain the download misses and license anomolies
  # for each indicator in one dataframe and saved as csv.
  process_report <- rbind(process_report,
                          c(k, download_misses, before_clean - after_clean))
  
  # For some reason, the column names were lost in the rbinding.
  names(process_report) <- c("ind", "download.misses","lic.nas")
  
  # Finally, our finished dataset for indicator-k.
  write.csv(final_set,
            file.path(
              getwd(),"exports", "performance",
              paste0(k, ".csv")))
  
} # End k (indicator)

# After we've downloaded all the data we could've, save process_report
# (the dataframe tracking the errors) as csv.
write.csv(process_report, file.path(getwd(), "exports","performance","process_report.csv"))

# Clean out library
remove(bank_data, url, i, j, k, indicator_IDs,
       months, years, end_month, end_year, time.end, time.start)


# Write the final data set into a csv for later use.
#write.csv(final_set, file.path(getwd(),"banki_data_perf.csv"))
