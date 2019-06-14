
# coding: utf-8

# # Add batch effects
# 
# Say we are interested in identifying genes that differentiate between disease vs normal states.  However our dataset includes samples from different tissues or time points and there are variations in gene expression that are due to these other conditions and do not have to do with disease state.  These non-relevant variations in the data are called *batch effects*.  
# 
# We want to model these batch effects.  To do this we will:
# 1. Partition our simulated data into n batches
# 2. For each partition we will randomly shift the expression data.  We randomly generate a binary vector of length=number of genes (*offset vector*).  This vector will serve as the direction that we will shift to.  Then we also have a random scalar that will tell us how big of a step to take in our random direction (*stretch factor*).  We shift our partitioned data by: batch effect partition = partitioned data + stretch factor * offset vector
# 3. Repeat this for each partition
# 4. Append all batch effect partitions together
# 

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import pandas as pd
import numpy as np
import random
import glob
import umap
import pickle
import warnings
warnings.filterwarnings(action='once')

from ggplot import *
from sklearn.decomposition import PCA
from numpy.random import seed
randomState = 123
seed(randomState)


# In[2]:


# Parameters
analysis_name = 'experiment_1'
NN_architecture = 'NN_2500_20'
num_simulations = 10
num_batches = [1,2,3,4,5,6,7,8,9,10,15,20,50,100,500,800]


# In[3]:


# Create directories
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../.."))

new_dir = os.path.join(
    base_dir,
    "data",
    "batch_simulated")

analysis_dir = os.path.join(new_dir, analysis_name)

if os.path.exists(analysis_dir):
    print('directory already exists: {}'.format(analysis_dir))
else:
    print('creating new directory: {}'.format(analysis_dir))
os.makedirs(analysis_dir, exist_ok=True)


# In[4]:


# Load arguments
simulated_data_file = os.path.join(
    base_dir,
    "data",
    "simulated",
    analysis_name,
    "simulated_data.txt")

simulated_data_mapping_file = os.path.join(
    base_dir,
    "data",
    "metadata",
    "mapping_simulated_data.txt")

umap_model_file = umap_model_file = os.path.join(
    base_dir,
    "models",  
    NN_architecture,
    "umap_model.pkl")


# In[5]:


# Read in UMAP model
infile = open(umap_model_file, 'rb')
umap_model = pickle.load(infile)
infile.close()


# In[6]:


# Read in data
simulated_data = pd.read_table(
    simulated_data_file,
    header=0, 
    index_col=0,
    sep='\t')

simulated_data.head(10)


# In[7]:


# Read in metadata
metadata = pd.read_table(
    simulated_data_mapping_file,
    header=0, 
    index_col=0,
    sep='\t')

metadata.head(10)


# In[8]:


# Replace NaN with string "NA"
metadata['metadata'] = metadata['metadata'].fillna('NA')


# In[9]:


# Add batch effects
# ADD MULTIPLE SIMULATION RUNS
num_simulated_samples = simulated_data.shape[0]
num_genes = simulated_data.shape[1]
subset_genes_to_change = np.random.RandomState(randomState).choice([0, 1], size=(num_genes), p=[0, 1])
    
for i in num_batches:
    print('Creating simulated data with {} batches..'.format(i))
    
    batch_file = os.path.join(
            base_dir,
            "data",
            "batch_simulated",
            analysis_name,
            "Batch_"+str(i)+".txt")
    
    num_samples_per_batch = int(num_simulated_samples/i)
    
    if i == 1:        
        simulated_data.to_csv(batch_file, sep='\t')
        
    else:  
        batch_data_df = pd.DataFrame()
        for j in range(i):
            
            stretch_factor = np.random.uniform(0,1)
            
            # Randomly select samples
            batch_df = simulated_data.sample(n=num_samples_per_batch, frac=None, replace=False)

            # Add batch effect
            subset_genes_to_change_tile = pd.DataFrame(
                pd.np.tile(
                    subset_genes_to_change,
                    (num_samples_per_batch, 1)),
                index=batch_df.index,
                columns=list(simulated_data.columns))
            

            offset_vector = pd.DataFrame(subset_genes_to_change_tile*stretch_factor,
                                         columns=list(simulated_data.columns))
            batch_df = batch_df + offset_vector

            # if any exceed 1 then set to 1 since gene expression is normalized
            batch_df[batch_df>=1.0] = 1.0


            # Append batched together
            batch_data_df = batch_data_df.append(batch_df)

            # Select a new direction (i.e. a new subset of genes to change)
            np.random.shuffle(subset_genes_to_change)
            
        # Save
        batch_data_df.to_csv(batch_file, sep='\t')


# ## Plot batch data using UMAP

# In[10]:


# Plot generated data in UMAP 

for i in num_batches:
    batch_data_file = os.path.join(
        base_dir,
        "data",
        "batch_simulated",
        analysis_name,
        "Batch_"+str(i)+".txt")
    
    batch_data = pd.read_table(
        batch_data_file,
        header=0,
        sep='\t',
        index_col=0)
    
    # Merge gene expression data and metadata
    batch_data_labeled = batch_data.merge(
        metadata,
        left_index=True, 
        right_index=True, 
        how='inner')

    print(batch_data_labeled.shape)
    
    # UMAP embedding of decoded batch data
    batch_data_UMAPencoded = umap_model.transform(batch_data_labeled.iloc[:,:-1])
    batch_data_UMAPencoded_df = pd.DataFrame(data=batch_data_UMAPencoded,
                                             index=batch_data_labeled.index,
                                             columns=['1','2'])
    batch_data_UMAPencoded_df['metadata'] = list(batch_data_labeled['metadata'])
    
        
    g = ggplot(aes(x='1',y='2', color='metadata'), data=batch_data_UMAPencoded_df) +                 geom_point(alpha=0.5) +                 scale_color_brewer(type='qual', palette='Set1') +                 ggtitle("{} Batches".format(i))
    
    print(g)
