#!/usr/bin/env python
# coding: utf-8

# # Visualize data
# 
# In order to start making interpretations we will generate two visualizations of our data
# 
# 1. We will verify that the simulated dataset is a good representation of our original input dataset by visually comparing the structures in the two datasets projected onto UMAP space.
# 
# 2. We will plot the PCA projected data after adding experiments to examine how the technical variation shifted the data.
# 
# 3. We plot the PCA projected data after correcting for the technical variation introduced by the experiments and examine the effectiveness of the correction method by comparing the data before and after the correction.

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import ast
import pandas as pd
import numpy as np
import random
import glob
from plotnine import (ggplot, 
                      geom_point, 
                      aes, 
                      labs,
                      facet_wrap, 
                      scale_colour_manual,
                      guides, 
                      guide_legend, 
                      theme_bw, 
                      theme,  
                      element_text,
                      element_rect,
                      ggsave)

from sklearn.decomposition import PCA
from keras.models import load_model
import umap

import warnings
warnings.filterwarnings(action='ignore')

from numpy.random import seed
randomState = 123
seed(randomState)


# In[2]:


# User parameters
NN_architecture = 'NN_2500_30'
analysis_name = 'analysis_1'
lst_num_partitions = [1,2,3,5,10,20,30,50,70,100]


# In[3]:


# Load data
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../.."))    # base dir on repo
local_dir = "/home/alexandra/Documents"                          # base dir on local machine for data storage

NN_dir = base_dir + "/models/" + NN_architecture
latent_dim = NN_architecture.split('_')[-1]

normalized_data_file = os.path.join(
    base_dir,
    "data",
    "input",
    "train_set_normalized.pcl")

model_encoder_file = glob.glob(os.path.join( ## Make more explicit name here
    NN_dir,
    "tybalt_2layer_{}latent_encoder_model.h5".format(latent_dim)))[0]

weights_encoder_file = glob.glob(os.path.join(
    NN_dir,
    "tybalt_2layer_{}latent_encoder_weights.h5".format(latent_dim)))[0]

model_decoder_file = glob.glob(os.path.join(
    NN_dir,
    "tybalt_2layer_{}latent_decoder_model.h5".format(latent_dim)))[0]

weights_decoder_file = glob.glob(os.path.join(
    NN_dir,
    "tybalt_2layer_{}latent_decoder_weights.h5".format(latent_dim)))[0]

partition_dir = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "partition_simulated",
    analysis_name)

simulated_data_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "simulated",
    analysis_name,
    "simulated_data.txt.xz")

permuted_simulated_data_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "simulated",
    analysis_name,
    "permuted_simulated_data.txt.xz")


# In[4]:


# Output files
umap_overlay_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_umap_overlay.png")

pca_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_pca_variation.png")

pca_correct_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_pca_correction.png")


# ## 1. Visualize simulated data in UMAP space

# In[5]:


# Load saved models
loaded_model = load_model(model_encoder_file)
loaded_decode_model = load_model(model_decoder_file)

loaded_model.load_weights(weights_encoder_file)
loaded_decode_model.load_weights(weights_decoder_file)


# In[6]:


# Read data
normalized_data = pd.read_table(
    normalized_data_file,
    header=0,
    sep='\t',
    index_col=0).T

simulated_data = pd.read_table(
    simulated_data_file,
    header=0,
    sep='\t',
    index_col=0)

simulated_data.drop(columns="experiment_id", inplace=True)

print(normalized_data.shape)
print(simulated_data.shape)


# In[7]:


normalized_data.head(10)


# In[8]:


simulated_data.head(10)


# In[9]:


# UMAP embedding of original input data

# Get and save model
model = umap.UMAP(random_state=randomState).fit(normalized_data)

input_data_UMAPencoded = model.transform(normalized_data)
input_data_UMAPencoded_df = pd.DataFrame(data=input_data_UMAPencoded,
                                         index=normalized_data.index,
                                         columns=['1','2'])


g_input = ggplot(input_data_UMAPencoded_df, aes(x='1',y='2'))     + geom_point(alpha=0.5)     + labs(x = "UMAP 1", y = "UMAP 2", title = "Input data") 
print(g_input)


# In[10]:


# UMAP embedding of simulated data
simulated_data_UMAPencoded = model.transform(simulated_data)
simulated_data_UMAPencoded_df = pd.DataFrame(data=simulated_data_UMAPencoded,
                                         index=simulated_data.index,
                                         columns=['1','2'])


g_sim = ggplot(simulated_data_UMAPencoded_df, aes(x='1',y='2'))     + geom_point(alpha=0.5)     + labs(x = "UMAP 1", y = "UMAP 2", title = "Simulated data") 
print(g_sim)


# In[11]:


# Side by side original input vs simulated data

# Add label for input or simulated dataset
input_data_UMAPencoded_df['dataset'] = 'original'
simulated_data_UMAPencoded_df['dataset'] = 'simulated'

# Concatenate input and simulated dataframes together
combined_data_df = pd.concat([input_data_UMAPencoded_df, simulated_data_UMAPencoded_df])

# Plot
ggplot(combined_data_df, aes(x='1', y='2')) + geom_point(alpha=0.3) + facet_wrap('~dataset') + labs(x = "UMAP 1", y = "UMAP 2", title = "UMAP of original and simulated data") 


# In[12]:


# Overlay original input vs simulated data

# Add label for input or simulated dataset
input_data_UMAPencoded_df['dataset'] = 'original'
simulated_data_UMAPencoded_df['dataset'] = 'simulated'

# Concatenate input and simulated dataframes together
combined_data_df = pd.concat([input_data_UMAPencoded_df, simulated_data_UMAPencoded_df])

# Plot
g_input_sim = ggplot(combined_data_df, aes(x='1', y='2')) + geom_point(aes(color='dataset'), alpha=0.3) + labs(x = "UMAP 1", y = "UMAP 2", title = "UMAP of original and simulated data") + theme_bw() + theme(
    legend_title_align = "center",
    plot_background=element_rect(fill='white'),
    legend_key=element_rect(fill='white', colour='white'), 
    plot_title=element_text(weight='bold')
) \
+ guides(colour=guide_legend(override_aes={'alpha': 1})) \
+ scale_colour_manual(["grey", '#87CEFA']) 

print(g_input_sim)
ggsave(plot = g_input_sim, filename = umap_overlay_file, dpi=300)


# ## 2. Visualize effects of multiple experiments in PCA space

# In[13]:


get_ipython().run_cell_magic('time', '', '\nall_data_df = pd.DataFrame()\n\n# Get batch 1 data\npartition_1_file = os.path.join(\n    partition_dir,\n    "Partition_1.txt.xz")\n\npartition_1 = pd.read_table(\n    partition_1_file,\n    header=0,\n    index_col=0,\n    sep=\'\\t\')\n\n\nfor i in lst_num_partitions:\n    print(\'Plotting PCA of 1 partition vs {} partition...\'.format(i))\n    \n    # Simulated data with all samples in a single partition\n    original_data_df =  partition_1.copy()\n    \n    # Add grouping column for plotting\n    original_data_df[\'num_partitions\'] = \'1\'\n    \n    # Get data with additional partitions added\n    partition_other_file = os.path.join(\n        partition_dir,\n        "Partition_"+str(i)+".txt.xz")\n\n    partition_other = pd.read_table(\n        partition_other_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n    \n    # Simulated data with i partitions\n    partition_data_df =  partition_other\n    \n    # Add grouping column for plotting\n    partition_data_df[\'num_partitions\'] = str(i)\n    \n    # Concatenate datasets together\n    combined_data_df = pd.concat([original_data_df, partition_data_df])\n\n    # PCA projection\n    pca = PCA(n_components=2)\n\n    # Encode expression data into 2D PCA space\n    combined_data_numeric_df = combined_data_df.drop([\'num_partitions\'], axis=1)\n    combined_data_PCAencoded = pca.fit_transform(combined_data_numeric_df)\n\n\n    combined_data_PCAencoded_df = pd.DataFrame(combined_data_PCAencoded,\n                                               index=combined_data_df.index,\n                                               columns=[\'PC1\', \'PC2\']\n                                              )\n                                              \n    # Variance explained\n    print(pca.explained_variance_ratio_)  \n    \n    # Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)\n    combined_data_PCAencoded_df[\'num_partitions\'] = combined_data_df[\'num_partitions\']\n    \n    # Add column that designates which batch effect comparision (i.e. comparison of 1 batch vs 5 batches\n    # is represented by label = 5)\n    combined_data_PCAencoded_df[\'comparison\'] = str(i)\n    \n    # Concatenate ALL comparisons\n    all_data_df = pd.concat([all_data_df, combined_data_PCAencoded_df])\n    \n    # Plot individual comparisons\n    print(ggplot(combined_data_PCAencoded_df, aes(x=\'PC1\', y=\'PC2\')) \\\n          + geom_point(aes(color=\'num_partitions\'), alpha=0.2) \\\n          + labs(x = "PC 1", y = "PC 2", title = "Partition 1 and Partition {}".format(i))\\\n          + theme_bw() \\\n          + theme(\n                legend_title_align = "center",\n                plot_background=element_rect(fill=\'white\'),\n                legend_key=element_rect(fill=\'white\', colour=\'white\'), \n                plot_title=element_text(weight=\'bold\')\n            ) \\\n          + guides(colour=guide_legend(override_aes={\'alpha\': 1})) \\\n          + scale_colour_manual(["grey", \'#87CEFA\'])\n         )             ')


# In[14]:


# Convert 'num_experiments' into categories to preserve the ordering
lst_num_partitions_str = [str(i) for i in lst_num_partitions]
num_partitions_cat = pd.Categorical(all_data_df['num_partitions'], categories=lst_num_partitions_str)

# Convert 'comparison' into categories to preserve the ordering
comparison_cat = pd.Categorical(all_data_df['comparison'], categories=lst_num_partitions_str)

# Assign to a new column in the df
all_data_df = all_data_df.assign(num_partitions_cat = num_partitions_cat)
all_data_df = all_data_df.assign(comparison_cat = comparison_cat)

# Rename header
all_data_df.columns = ['PC1', 'PC2', 'num_partitions', 'comparison', 'No. of partitions', 'Comparison']


# In[15]:


# Plot all comparisons in one figure
g_pca = ggplot(all_data_df, aes(x='PC1', y='PC2')) + geom_point(aes(color='No. of partitions'), alpha=0.1) + facet_wrap('~Comparison') + labs(x = "PC 1", y = "PC 2", title = "PCA of experiment 1 vs multiple experiments") + theme_bw() + theme(
    legend_title_align = "center",
    plot_background=element_rect(fill='white'),
    legend_key=element_rect(fill='white', colour='white'), 
    plot_title=element_text(weight='bold')
) \
+ guides(colour=guide_legend(override_aes={'alpha': 1})) \
+ scale_colour_manual(["grey", '#87CEFA', '#e6beff', '#ffe119', '#4363d8', '#FFA500', 
                      '#911eb4', '#B0E0E6', '#f032e6', '#bcf60c', '#fabebe', '#008080'])

print(g_pca)
ggsave(plot = g_pca, filename = pca_file, dpi=300)


# ## Visualize multiple experiments in UMAP space

# In[16]:


get_ipython().run_cell_magic('time', '', '\nall_data_df = pd.DataFrame()\n\n# Get batch 1 data\npartition_1_file = os.path.join(\n    partition_dir,\n    "Partition_1.txt.xz")\n\npartition_1 = pd.read_table(\n    partition_1_file,\n    header=0,\n    index_col=0,\n    sep=\'\\t\')\n\n\nfor i in lst_num_partitions:\n    print(\'Plotting UMAP of 10-PCA of 1 partition vs {} partitions...\'.format(i))\n    \n    # Simulated data with all samples in a single batch\n    original_data_df =  partition_1.copy()\n    \n    # Add grouping column for plotting\n    original_data_df[\'group\'] = \'partition_1\'\n    \n    # Get data with additional partitions added\n    partition_other_file = os.path.join(\n        partition_dir,\n        "Partition_"+str(i)+".txt.xz")\n\n    partition_other = pd.read_table(\n        partition_other_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n    \n    # Simulated data with i partitions\n    partition_data_df =  partition_other\n    \n    # Add grouping column for plotting\n    partition_data_df[\'group\'] = "partition_{}".format(i)\n    \n    # Concatenate datasets together\n    combined_data_df = pd.concat([original_data_df, partition_data_df])\n    \n    # PCA projection\n    pca = PCA(n_components=10)\n\n    # Encode expression data into 2D PCA space\n    combined_data_numeric_df = combined_data_df.drop([\'group\'], axis=1)\n    combined_data_PCAencoded = pca.fit_transform(combined_data_numeric_df)\n\n\n    combined_data_PCAencoded_df = pd.DataFrame(combined_data_PCAencoded,\n                                               index=combined_data_df.index,\n                                              )\n    \n    # Variance explained\n    print(pca.explained_variance_ratio_)  \n                                              \n   \n    # Encode 10-dim PCA compressed expression data into UMAP space\n    combined_data_UMAPencoded = umap.UMAP(random_state=randomState).fit_transform(combined_data_PCAencoded_df)\n    combined_data_UMAPencoded_df = pd.DataFrame(data=combined_data_UMAPencoded,\n                                             index=combined_data_PCAencoded_df.index,\n                                             columns=[\'UMAP1\',\'UMAP2\'])\n    \n    \n    # Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)\n    combined_data_UMAPencoded_df[\'group\'] = combined_data_df[\'group\']\n    \n    # Add column that designates which batch effect comparision (i.e. comparison of 1 batch vs 5 batches\n    # is represented by label = 5)\n    combined_data_UMAPencoded_df[\'num_partitions\'] = str(i)\n    \n    # Concatenate ALL comparisons\n    all_data_df = pd.concat([all_data_df, combined_data_UMAPencoded_df])\n    \n    # Plot individual comparisons\n    print(ggplot(combined_data_UMAPencoded_df, aes(x=\'UMAP1\', y=\'UMAP2\')) \\\n          + geom_point(aes(color=\'group\'), alpha=0.2) \\\n          + labs(x = "UMAP 1", y = "UMAP 2", title = "UMAP of partition 1 vs partition {}".format(i)) \\\n         )')


# In[17]:


# Plot all comparisons in one figure
ggplot(all_data_df, aes(x='UMAP1', y='UMAP2')) + geom_point(aes(color='group'), alpha=0.2) + facet_wrap('~num_partitions') + labs(x = "UMAP 1", y = "UMAP 2", title = "UMAP of partition 1 vs partition x") 


# **Note:** 
# 
# 1. We are using PCA space to visualize the simulated data with different numbers of experiments added in order to detect the effect of the variance added by the different experiments.  UMAP is focused on trying to find the optimal low dimensional representation of the data that preserves the topological structures in the data in high dimensional space.  
# 
# 2. In order to examine the structure that is captured in using 10 PCs (set by the user), we plotted the UMAP projection of the gene expression data compressed into the top 10 PCs.  We can see that there is some structure in the 10-PCA data.

# ## 3. Visualize variance corrected experiment data

# In[18]:


get_ipython().run_cell_magic('time', '', '\nall_data_df = pd.DataFrame()\n\nfor i in lst_num_partitions:\n    print(\'Plotting PCA of 1 partition vs {} partitions...\'.format(i))\n    \n    # Get data BEFORE correction\n    partition_before_file = os.path.join(\n        partition_dir,\n        "Partition_"+str(i)+".txt.xz")\n\n    partition_before = pd.read_table(\n        partition_before_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n    \n    # Match format of column names in before and after df\n    partition_before.columns = partition_before.columns.astype(str)\n    \n    # Add grouping column for plotting\n    partition_before[\'correction\'] = "before"\n    \n    # Get data AFTER correction\n    partition_after_file = os.path.join(\n        partition_dir,\n        "Partition_corrected_"+str(i)+".txt.xz")\n\n    partition_after = pd.read_table(\n        partition_after_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n    \n    # Transpose data to df: sample x gene\n    partition_after = partition_after.T\n    \n    # Match format of column names in before and after df\n    #experiment_after.columns = experiment_after.columns.astype(str)\n    \n    # Add grouping column for plotting\n    partition_after[\'correction\'] = "after"\n        \n    # Concatenate datasets together\n    combined_data_df = pd.concat([partition_before, partition_after])\n    \n    # PCA projection\n    pca = PCA(n_components=2)\n\n    # Encode expression data into 2D PCA space    \n    combined_data_numeric_df = combined_data_df.drop([\'correction\'], axis=1)    \n    combined_data_PCAencoded = pca.fit_transform(combined_data_numeric_df)\n\n    \n    combined_data_PCAencoded_df = pd.DataFrame(combined_data_PCAencoded,\n                                               index=combined_data_df.index,\n                                               columns=[\'PC1\', \'PC2\']\n                                              )\n    \n    # Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)\n    combined_data_PCAencoded_df[\'correction\'] = combined_data_df[\'correction\']\n    \n    # Add column that designates which batch effect comparision (i.e. comparison of 1 batch vs 5 batches\n    # is represented by label = 5)\n    combined_data_PCAencoded_df[\'num_partitions\'] = str(i)\n    \n    # Concatenate ALL comparisons\n    all_data_df = pd.concat([all_data_df, combined_data_PCAencoded_df])\n    \n    # Split dataframe in order to plot \'after\' on top of \'before\'\n    df_layer_1 = combined_data_PCAencoded_df[combined_data_PCAencoded_df[\'correction\'] == "before"]\n    df_layer_2 = combined_data_PCAencoded_df[combined_data_PCAencoded_df[\'correction\'] == "after"]\n\n    \n    # Plot individual comparisons\n    print(ggplot(combined_data_PCAencoded_df, aes(x=\'PC1\', y=\'PC2\')) \\\n          + geom_point(aes(color=\'correction\'), alpha=0.2) \\\n          + geom_point(df_layer_1, aes(color=[\'before\']), alpha=0.2) \\\n          + geom_point(df_layer_2, aes(color=[\'after\']), alpha=0.2) \\\n          + labs(x = "PC 1", y = "PC 2", title = "Partition {} and Corrected Partition {}".format(i, i)) \\\n          + theme_bw() \\\n          + theme(\n                legend_title_align = "center",\n                plot_background=element_rect(fill=\'white\'),\n                legend_key=element_rect(fill=\'white\', colour=\'white\'),\n                plot_title=element_text(weight=\'bold\')) \\\n          + scale_colour_manual(["grey", \'#87CEFA\'])\n         )')


# In[19]:


# Convert 'comparison' into categories to preserve the ordering
num_partitions_cat = pd.Categorical(all_data_df['num_partitions'], categories=lst_num_partitions_str)

# Assign to a new column in the df
all_data_df = all_data_df.assign(num_partitions_cat = num_partitions_cat)


# In[20]:


# Plot all comparisons in one figure

# Split dataframe in order to plot 'after' on top of 'before'
df_layer_1 = all_data_df[all_data_df['correction'] == "before"]
df_layer_2 = all_data_df[all_data_df['correction'] == "after"]

g_correct = ggplot(all_data_df, aes(x='PC1', y='PC2')) + geom_point(aes(color='correction'), alpha=0.2) + geom_point(df_layer_1, aes(color=['before']), alpha=0.2) + geom_point(df_layer_2, aes(color=['after']), alpha=0.2) + facet_wrap('~num_partitions_cat') + labs(x = "PC 1", y = "PC 2", title = "PCA after correcting for partition variation") + theme_bw() + theme(
    legend_title_align = "center",
    plot_background=element_rect(fill='white'),
    legend_key=element_rect(fill='white', colour='white'), 
    plot_title=element_text(weight='bold')) \
+ guides(colour=guide_legend(override_aes={'alpha': 1})) \
+ scale_colour_manual(["grey", '#87CEFA'])

print(g_correct)
ggsave(plot = g_correct, filename = pca_correct_file, dpi=300)


# ## Permuted dataset (Negative control)
# 
# As a negative control we will permute the values within a sample, across genes in order to disrupt the gene expression structure.

# In[21]:


# Read in permuated data
shuffled_simulated_data = pd.read_table(
    permuted_simulated_data_file,
    header=0,
    index_col=0,
    sep='\t')


# In[22]:


# Label samples with label = perumuted
shuffled_simulated_data['group'] = "permuted"

# Concatenate original simulated data and shuffled simulated data
input_vs_permuted_df = pd.concat([original_data_df, shuffled_simulated_data])


input_vs_permuted = input_vs_permuted_df.drop(['group'], axis=1)
shuffled_data_PCAencoded = pca.fit_transform(input_vs_permuted)


shuffled_data_PCAencoded_df = pd.DataFrame(shuffled_data_PCAencoded,
                                           index=input_vs_permuted_df.index,
                                           columns=['PC1', 'PC2']
                                          )

# Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)
shuffled_data_PCAencoded_df['group'] = input_vs_permuted_df['group']


# In[23]:


# Plot permuted data
print(ggplot(shuffled_data_PCAencoded_df, aes(x='PC1', y='PC2'))       + geom_point(aes(color='group'), alpha=0.2)       + labs(x = "PC 1", y = "PC 2", title = "Simulated vs Permuted")      )
