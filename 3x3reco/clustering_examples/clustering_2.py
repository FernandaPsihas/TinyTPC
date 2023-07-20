from sklearn.datasets import make_blobs
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings("ignore")


# create blobs
data = make_blobs(n_samples=200, n_features=2, centers=4, cluster_std=1.6, random_state=50)

# create np array for fata points
points = data[0]

# create scatter plot
plt.scatter(data[0][:,0], data[0][:,1], c=data[1], cmap='viridis')
plt.xlim(-15, 15)
plt.ylim(-15,15)
plt.show()

#create kmeans object
kmeans = KMeans(n_clusters=4)

#fit kmeans object to data
kmeans.fit(points)

#print location of clusters learned by kmeans object
print(kmeans.cluster_centers_)

#save new clusters for chart
y_km = kmeans.fit_predict(points)

#now running the code in matplotlib to see the results

plt.scatter(points[y_km ==0,0], points[y_km == 0,1], s=100, c='red')
plt.scatter(points[y_km ==1,0], points[y_km == 1,1], s=100, c='black')
plt.scatter(points[y_km ==2,0], points[y_km == 2,1], s=100, c='blue')
plt.scatter(points[y_km ==3,0], points[y_km == 3,1], s=100, c='cyan')
plt.show()
