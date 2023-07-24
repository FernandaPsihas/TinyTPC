import pandas as pd #this for data manipulation and importing data files

from sklearn.cluster import DBSCAN #for building a clustering model
from sklearn.preprocessing import MinMaxScaler #for feature scaling
from sklearn import metrics #for calculating the silhouette score

import matplotlib.pyplot as plt #for data visualization 
import plotly.graph_objects as go #for data visualization
import plotly.express as px #for data visulaization
import plotly.offline as po #to print figures

#reading the sample data that I downloaded

df = pd.read_csv('/Users/eunicebeato/Downloads/Real_estate.csv', encoding='utf-8')


# Create a 3D scatter plot
fig = px.scatter_3d(df, x=df['X3 distance to the nearest MRT station'], y=df['X2 house age'], z=df['Y house price of unit area'], 
                 opacity=1, color_discrete_sequence=['black'], height=900, width=900)

# Update chart looks
fig.update_layout(#title_text="Scatter 3D Plot",
                  scene_camera=dict(up=dict(x=0, y=0, z=1), 
                                        center=dict(x=0, y=0, z=-0.2),
                                        eye=dict(x=1.5, y=1.5, z=0.5)),
                                        margin=dict(l=0, r=0, b=0, t=0),
                  scene = dict(xaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         ),
                               yaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                          ),
                               zaxis=dict(backgroundcolor='lightgrey',
                                          color='black', 
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         )))

# Update marker size
fig.update_traces(marker=dict(size=2))

fig.show()
fig.write_image('fig0_.pdf')
po.plot(fig, filename='fig0_.html')


# Select data
X = df[['X3 distance to the nearest MRT station','X2 house age', 'Y house price of unit area']]

# Plot distribution charts
fig, axs = plt.subplots(1, 3) #figsize=(16,4), dpi=300)
axs[0].hist(X.iloc[:,0], bins=50, color='black', rwidth=0.9)
axs[0].set_title('X3 distance to the nearest MRT station')
axs[1].hist(X.iloc[:,1], bins=50, color='black', rwidth=0.9)
axs[1].set_title('X2 house age')
axs[2].hist(X.iloc[:,2], bins=50, color='black', rwidth=0.9)
axs[2].set_title('Y house price of unit area')
plt.show()


# Apply MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Plot distribution charts
fig, axs = plt.subplots(1, 3) #figsize=(16,4), dpi=300)
axs[0].hist(X_scaled[:,0], bins=50, color='black', rwidth=0.9)
axs[0].set_title('X3 distance to the nearest MRT station')
axs[1].hist(X_scaled[:,1], bins=50, color='black', rwidth=0.9)
axs[1].set_title('X2 house age')
axs[2].hist(X_scaled[:,2], bins=50, color='black', rwidth=0.9)
axs[2].set_title('Y house price of unit area')
plt.show()


# Create empty lists
S=[] # this is to store Silhouette scores
comb=[] # this is to store combinations of epsilon / min_samples

# Define ranges to explore
eps_range=range(6,12) # note, we will scale this down by 100 as we want to explore 0.06 - 0.11 range
minpts_range=range(3,8)

for k in eps_range:
    for j in minpts_range:
        # Set the model and its parameters
        model = DBSCAN(eps=k/100, min_samples=j)
        # Fit the model 
        clm = model.fit(X_scaled)
        # Calculate Silhoutte Score and append to a list
        S.append(metrics.silhouette_score(X_scaled, clm.labels_, metric='euclidean'))
        comb.append(str(k)+"|"+str(j)) # axis values for the graph

# Plot the resulting Silhouette scores on a graph
plt.figure() #figsize=(16,8), dpi=300)
plt.plot(comb, S, 'bo-')
plt.xlabel('Epsilon/100 | MinPts')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score based on different combnation of Hyperparameters')
plt.show()



# ------- DBSCAN -------
# Set up model parameters 

# First model: eps=0.08, MinPts=3
model83 = DBSCAN(eps=0.08, # default=0.5, The maximum distance between two samples for one to be considered as in the neighborhood of the other.
               min_samples=3, # default=5, The number of samples (or total weight) in a neighborhood for a point to be considered as a core point.
               metric='euclidean', # default='euclidean'. The metric to use when calculating distance between instances in a feature array. 
               metric_params=None, # default=None, Additional keyword arguments for the metric function.
               algorithm='auto', # {‘auto’, ‘ball_tree’, ‘kd_tree’, ‘brute’}, default=’auto’, The algorithm to be used by the NearestNeighbors module to compute pointwise distances and find nearest neighbors.
               leaf_size=30, # default=30, Leaf size passed to BallTree or cKDTree.
               p=None, # default=None, The power of the Minkowski metric to be used to calculate distance between points. If None, then p=2
               n_jobs=None, # default=None, The number of parallel jobs to run. None means 1 unless in a joblib.parallel_backend context. -1 means using all processors.
              )

# Second model: eps=0.06, MinPts=6
model66 = DBSCAN(eps=0.06, min_samples=6) # note, as above this uses default value for other parameters

# Fit the models
clm83 = model83.fit(X_scaled)
clm66 = model66.fit(X_scaled)

# Print DBSCAN results
print('*************** DBSCAN Clustering Model ***************')
print("Cluster labels for the first model")
print(clm83.labels_)
print("Cluster labels for the second model")
print(clm66.labels_)

df['DBSCAN Clusters 83']=clm83.labels_
df['DBSCAN Clusters 66']=clm66.labels_
print(df)


# Sort the dataframe so clusters in the legend follow the number order
df=df.sort_values(by=['DBSCAN Clusters 83'])

# Create a 3D scatter plot
fig = px.scatter_3d(df, x=df['X3 distance to the nearest MRT station'], y=df['X2 house age'], z=df['Y house price of unit area'], 
                    opacity=1, color=df['DBSCAN Clusters 83'].astype(str), 
                    color_discrete_sequence=['black']+px.colors.qualitative.Plotly,
                    hover_data=['X5 latitude', 'X6 longitude'],
                    width=900, height=900
                   )

# Update chart looks
fig.update_layout(#title_text="Scatter 3D Plot",
                  showlegend=True,
                  legend=dict(orientation="h", yanchor="bottom", y=0.04, xanchor="left", x=0.1),
                  scene_camera=dict(up=dict(x=0, y=0, z=1), 
                                        center=dict(x=0, y=0, z=-0.2),
                                        eye=dict(x=1.5, y=1.5, z=0.5)),
                                        margin=dict(l=0, r=0, b=0, t=0),
                  scene = dict(xaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         ),
                               yaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                          ),
                               zaxis=dict(backgroundcolor='lightgrey',
                                          color='black', 
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         )))
# Update marker size
fig.update_traces(marker=dict(size=2))

fig.show()
fig.write_image('fig1_.pdf')
po.plot(fig, filename='fig1_.html')



# Sort the dataframe so clusters in the legend follow the number order
df=df.sort_values(by=['DBSCAN Clusters 66'])

# Create a 3D scatter plot
fig = px.scatter_3d(df, x=df['X3 distance to the nearest MRT station'], y=df['X2 house age'], z=df['Y house price of unit area'], 
                    opacity=1, color=df['DBSCAN Clusters 66'].astype(str), 
                    color_discrete_sequence=['black']+px.colors.qualitative.Plotly,
                    hover_data=['X5 latitude', 'X6 longitude'],
                    width=900, height=900
                   )

# Update chart looks
fig.update_layout(#title_text="Scatter 3D Plot",
                  showlegend=True,
                  legend=dict(orientation="h", yanchor="bottom", y=0.04, xanchor="left", x=0.1),
                  scene_camera=dict(up=dict(x=0, y=0, z=1), 
                                        center=dict(x=0, y=0, z=-0.2),
                                        eye=dict(x=1.5, y=1.5, z=0.5)),
                                        margin=dict(l=0, r=0, b=0, t=0),
                  scene = dict(xaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         ),
                               yaxis=dict(backgroundcolor='white',
                                          color='black',
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                          ),
                               zaxis=dict(backgroundcolor='lightgrey',
                                          color='black', 
                                          gridcolor='#f0f0f0',
                                          title_font=dict(size=10),
                                          tickfont=dict(size=10),
                                         )))
# Update marker size
fig.update_traces(marker=dict(size=2))

fig.show()
fig.write_image('fig2_.pdf')
po.plot(fig, filename='fig2_.html')
