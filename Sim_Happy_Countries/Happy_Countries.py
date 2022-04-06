
from scipy.cluster.hierarchy import dendrogram
import scipy.spatial.distance

from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering, KMeans, k_means
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt


df = pd.read_csv("2021.csv")
matrix = df[["Healthy life expectancy", "Ladder score"]]

# Inertia scores to choose a good cluster number

inertia_scores = []
svd = TruncatedSVD(n_components=1)
svd.fit(matrix)

matrix_reduced_pt2 = svd.transform(matrix)
# redo clustering with random k values

# Let us test different values of k
inertia_scores = []
for test_k in set(np.random.randint(2, 120, 30)):
    print(test_k)

    tmp_model = KMeans(n_clusters=test_k)
    tmp_model.fit(matrix_reduced_pt2)

    score = tmp_model.inertia_
    inertia_scores.append((test_k, score))
intertia_df = pd.DataFrame(inertia_scores, columns=["k", "score"])
fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(1, 1, 1)

intertia_df.sort_values(by="k").plot("k", "score", ax=ax)
print(intertia_df)
ax.set_ylabel("Intertia")
plt.show()  # "Elbow" graph


# uncomment KMeans(..) and comment AgglomerativeClustering(...) to choose between the two models
# model = KMeans(n_clusters=20)
num_clusters = 20  # 20 is from inertia score
model = AgglomerativeClustering(n_clusters=num_clusters)
model.fit(matrix)
df["cluster"] = model.labels_

plt.scatter(matrix["Ladder score"],
            matrix["Healthy life expectancy"], c=df["cluster"])
plt.show()  # scatterplot


counter = 0
while counter < num_clusters:
    df2 = df.loc[df["cluster"] == counter]
    print("CLUSTER:", counter)
    print(df2[["Country name", "Regional indicator",
          "Healthy life expectancy", "Ladder score"]])
    print(df2["Regional indicator"].value_counts())
    counter += 1
newdf = df.set_index('Country name')
newdf = df.loc[df["cluster"] == 19]
newdf = newdf[["Healthy life expectancy", "Ladder score"]]

newdf["points"] = list(
    zip(newdf["Healthy life expectancy"], newdf["Ladder score"]))
points = newdf["points"].values.tolist()

sim = scipy.spatial.distance.cdist(points, points, 'euclidean')
cluster_list = ['United States', 'Lithuania', "Colombia", "Hungary",
                "Nicaragua", "Peru", "Bosnia and Herzegovina", "Vietnam"]
simdf = pd.DataFrame(sim, columns=cluster_list)
simdf["Country Name"] = cluster_list
simdf = simdf.set_index("Country Name")
print(simdf)


# Dendrogram to show hierarchy of AgglomerativeClustering


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


# setting distance_threshold=0 ensures we compute the full tree.
model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)

model = model.fit(matrix)
fig = plt.figure(figsize=(16, 9))
plt.title("Hierarchical Clustering Dendrogram")
# plot the top three levels of the dendrogram
plot_dendrogram(model, truncate_mode="level", p=3)
plt.ylabel("Distance")
plt.xlabel("Number of points in node (or index of point if no parenthesis).")
plt.show()
