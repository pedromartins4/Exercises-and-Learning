# Exercises on Machine Learning

This contains a set of tutorials and exercises related with all the phases of data science and machine learning: data cleaning, treatment, preparation, modeling and analysis. 

These files contain side-notes and experiences.

### sklearn

* `linear-regression.ipynb` Is a very simple tutorial with sklearn predictors. Uses regular and k-neighbors linear regression and does basic matplotlit plotting.

* `housing-prices.ipynb` Has and end-to-end ML process with all the phases from data extraction to prediction.
  * Geographical presentation of data.
  * Plot of variable distributions and correlations with matplotlib.
  * Full implementation of data processing pipeline using sklearn Pipeline class (split into categorical and numerical variables, filling gaps, standardization and normalization, scaling).
  * Explores regression using sklearn predictors: simple regression, decision tree and random forests. All models rated and validated with cross-validation.
  * Automatic hyperparameter tuning for prediction models.
  * Model validation.

* `mnist-classification.ipynb` Explores classification.
  * Classification with SGDClassifier and random forests from sklearn.
  * Classifier evaluation with cross-validation.
  * Analysis of precision/recall tradeoff, F1 score.
  * Model comparison with ROC curve and score.
  * Multiclass prediction implementation with binary classifier, using OvO and OvA strategies.
  * Multiclass model evaluation with confusion matrix.
  * Multilabel prediction implementation with KNeighbors.
  * Multioutput classification with KNeighbors.

* `iris-SVM.ipynb` Exercises with support vector machine.
  * Exercises on regression and classification using SVM.
  * Linear and non-linear classification.
  * Non-linear classification with polynomial and gaussian kernel.
  * SVM applied to MNIST (data scaling, params tuning with grid search, cross-validation).

* `iris-decision-trees.ipynb` Exercise on Decision Trees.
  * Application on iris dataset.
  * visualization of boundary definitions.
  * Class estimation.

* `ensemble-random-forests.ipynb` Exercises on Ensemble methods with special focus on random forests and boosting.
  * Multi-predictor ensemble with soft and hard voting.
  * Exercises on boosting and pasting.
  * Ensemble evaluation with out-of-box instances.
  * Random forest applied to MNIST and Moons datasets.
  * Feature importance analysis from random forestsm with MNIST pixel importance visualization.
  * Boosting with AdaBoost
  * Boosting with Gradient Boosting with analysis of learning rate
  * Finding best number of constintuents with staged_predict() and early stopping

* `p-component-analysis.ipynb` Exercises on dimentionality reduction, for visualization or analysis.
  * Principal Component Analysis (PCA) using sklearn.
  * To and for dimension transformations.
  * Analysis of variance impact by PCA.

### tensorflow

* `tensorflow-intro.ipynb` Introduction to tensorflow.
  * Linear regression with tensorflow.
  * Manual implementation of gradient descent and autodiff.
  * Feeding batch data into tensorflow.
  * Save and restore models.
  * Model visualizationm with tensorboard.
  * Full end-to-end implementation of analysis of Moons dataset.
  
  
