# Import all the libraries we'll be using
import numpy as np
import statsmodels.api as sm
from statsmodels import regression, stats
import statsmodels
import matplotlib.pyplot as plt

residuals = np.random.normal(0, 1, 100)
_, pvalue, _, _ = statsmodels.stats.stattools.jarque_bera(residuals)
print('Data is normal:', pvalue)

residuals = np.random.poisson(size=100)
_, pvalue, _, _ = statsmodels.stats.stattools.jarque_bera(residuals)
print('Data is not normal:', pvalue)

# Artificially create dataset with constant variance around a line
xs = np.arange(100)
y1 = xs + 3 * np.random.randn(100)

# Get results of linear regression
slr1 = regression.linear_model.OLS(y1, sm.add_constant(xs)).fit()

# Construct the fit line
fit1 = slr1.params[0] + slr1.params[1] * xs

# Plot data and regression line
plt.scatter(xs, y1)
plt.plot(xs, fit1)
plt.title('Homoskedastic errors')
plt.legend(['Predicted', 'Observed'])
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

# Print summary of regression results
print(slr1.summary())

# Artificially create dataset with changing variance around a line
y2 = xs * (1 + .5 * np.random.randn(100))

# Perform linear regression
slr2 = regression.linear_model.OLS(y2, sm.add_constant(xs)).fit()
fit2 = slr2.params[0] + slr2.params[1] * xs

# Plot data and regression line
plt.scatter(xs, y2)
plt.plot(xs, fit2)
plt.title('Heteroskedastic errors')
plt.legend(['Predicted', 'Observed'])
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

# Print summary of regression results
print(slr2.summary())
