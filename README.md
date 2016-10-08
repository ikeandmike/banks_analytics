# banks_analytics

A suite of programs to evaluate RandomForestClassifier and LogisticRegression for the purpose of predicting license revocation of banks in the Russian Federation.

## About
* This project was developed as part of an Interactive Qualifying Project for Worcester Polytechnic Institute.
* The project was completed by Jacob Bortell, Michael Giancola, Everett Harding, and Parmenion Patias between August and October 2016.
* The work was done at the Financial University and Deloitte Analytics Institute in Moscow, Russia.
* The model utilizes the [scikit-learn library](https://scikit-learn.org/stable/) for Python.

## How to Run it
* Before running, the model has the following dependencies:
	* Python (Version >= 2.6)
	* Scikit-learn (Version >= 0.18)
	* Numpy (Version >= 1.6.1)
	* Scipy (Version 0.9)
	* Pandas
* To run the model, cd into the `model` folder, and execute `python model.py`

## How it Works
Our model uses internal indicators to predict the probability of revoking banking licenses. We download statistics from Banki.ru and the Central Bank of Russia to use as features for the models, and manually calculate the months until revocation as the target variable.

## Parser
* To download data for the model, run `python parser.py`. Running it with `-h` will explain further how to receive the data as you wish.
* Within the `csv` folder, there are four files:
	* banki.csv contains all of the raw indicator data downloaded by the parser
	* banki_revoked.csv contains all of the revocation dates
	* banki_complete.csv contains the cleaned version of the above two files, which has calculated the number of months until revocation
	* model_data.csv contains a subset of the indicators, if specified by calling the parser with the `-s` option. Otherwise, this file is identical to banki_complete.csv

## Model
The model is comprised of several files, all located in the `model` folder.
* model.py is the main program file.
* ModelResults.py contains a definition for the ModelResults class, which is used to store (and eventually export) the results of model execution.
* export_test.py contains code for exporting results from the model. This is used by model.py
* rand_test.py is a small script for generating scores for precision/recall/F1 on a set of results where the predictions were made by a random number generator. We used this to give a baseline comparison of our models vs. random guessing.
* c_test.py is a script for testing C values of LogisticRegression.

## Results
From our comparison we found that RandomForest always outperformed LogisticRegression. For full results, including all datasets, graphs, and our analysis, see our report on WPI's website (link to come later).
