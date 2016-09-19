# banks_analytics

## About
* This project was developed as part of an Interactive Qualifying Project for Worcester Polytechnic Institute.
* The project was completed by Jacob Bortell, Michael Giancola, Everett Harding, and Parmenion Patias from August to October 2016.
* The work was done at the Financial University and Deloitte Analytics Institute in Moscow, Russia.

Our model uses internal indicators to predict the probability of revoking banking licenses.

## Parser
* To download data for the model, run `python parser.py`. Running it with `-h` will explain further how to receive the data as you wish.
* Within the `csv` folder, there are four files:
	* banki.csv contains all of the raw indicator data downloaded by the parser
	* banki_revoked.csv contains all of the revocation dates
	* banki_complete.csv contains the cleaned version of the above two files, which has calculated the number of months until revocation
	* model_data.csv contains a subset of the indicators, if specified by calling the parser with the `-s` option. Otherwise, this file is identical to banki_complete.csv


## Model
* To run the model, execute `python multinomial_logistic_regression.py` in the `banks_analytics` folder.

TODO Add more details about comparing C values, output.
