import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 1. Datos
X = np.arange(15).reshape(-1, 1)
y = 2 * X.flatten() + 3 + np.random.randn(15)

# 2. Modelo
model = LinearRegression()
model.fit(X, y)
print("R²:", model.score(X, y))


# 3. Coeficientes
print(f"Pendiente (coef_): {model.coef_[0]}")
print(f"Intercepto (intercept_): {model.intercept_}")

# 4. Predicción
X_new = np.array([[6]])
y_pred = model.predict(X_new)
print(f"Predicción para X=6: {y_pred[0]}")

# 5. Visualización
plt.scatter(X, y, color="red")
plt.plot(X, model.predict(X))
plt.title('Regresión Lineal Simple')
plt.show()
