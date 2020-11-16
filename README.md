# Msc-Thesis-Explanations
The code repository including all scripts and results from my master thesis research, "A Quantitative Comparison of LocalExplanation Methods".
The thesis completes my Master Econometrics, Quantitative Marketing and Business Analytics, at the Erasmus School of Economics, Erasmus University Rotterdam.

Research was done in combination with an internship at Viqtor Davis NL, supervised by dr. Bram Bet.
Acadamic supervision was done by  prof. dr. Ilker Birbil.

The main topic of my thesis is a twofold comparison of four methods. The Logistic Regression, Supersparse Linear Integer Model, Explainable Boosting Machine and SHAP are all evaluated based on both their predictive performance and their explanation quality. Additionally synthetically created data is used to further explore the different methods and a survey among data scientists is held to provide some human context.


The *research* folder contains the main research.
It is subdivided into five other folders:
- *data* contains all different data sets used in the research
- *notebooks* contains the main scripts used in training and evaluating the different models as well as the synthetic data part.
- *results* contains trained pickled models or data and saved plots
- *slim_packages* contains two customised implementations of SLIM, one using up-to-date Python 3.7, the other implementing ORTools as MIP solver instead of CPLEX. Both are an adaptation of the original python package from [Berk Ustun](https://github.com/ustunb/slim-python)
- *synthetic_data* is a folder containing the synthetically generated data along with 'true explanations' and corresponding trained models
The *survey* folder contains the survey, survey results and a script for some basic analysis
