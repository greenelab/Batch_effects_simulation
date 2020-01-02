'''
Author: Alexandra Lee
Date Created: 11 November 2019

Scripts to run all scripts in one function in order to run the entire pipeline multiple times in parallel
'''
import os
import sys
import glob
import pickle
import pandas as pd
import numpy as np

import rpy2
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
limma = importr('limma')

import warnings
warnings.filterwarnings(action='ignore')

sys.path.append("../")
from functions import generate_data_parallel
from functions import similarity_metric_parallel


def simple_simulation_experiment_uncorrected(run,
                                             NN_architecture,
                                             analysis_name,
                                             num_simulated_samples,
                                             lst_num_experiments,
                                             corrected,
                                             use_pca,
                                             num_PCs,
                                             file_prefix,
                                             input_file):

  # Input files
  local_dir = "/home/alexandra/Documents/"

  # Main

  # Generate simulated data
  simulated_data = generate_data_parallel.simulate_data(input_file,
                                                        NN_architecture,
                                                        analysis_name,
                                                        num_simulated_samples
                                                        )

  # Permute simulated data to be used as a negative control
  permuted_data = generate_data_parallel.permute_data(simulated_data,
                                                      local_dir,
                                                      analysis_name)

  # Add technical variation
  generate_data_parallel.add_experiments_io(simulated_data,
                                            lst_num_experiments,
                                            run,
                                            local_dir,
                                            analysis_name)

  # Calculate similarity between compendium and compendium + noise
  batch_scores, permuted_score = similarity_metric_parallel.sim_svcca_io(simulated_data,
                                                                         permuted_data,
                                                                         corrected,
                                                                         file_prefix,
                                                                         run,
                                                                         lst_num_experiments,
                                                                         use_pca,
                                                                         num_PCs,
                                                                         local_dir,
                                                                         analysis_name)

  # Convert similarity scores to pandas dataframe
  similarity_score_df = pd.DataFrame(data={'score': batch_scores},
                                     index=lst_num_experiments,
                                     columns=['score'])

  similarity_score_df.index.name = 'number of experiments'
  similarity_score_df

  # Return similarity scores and permuted score
  return permuted_score, similarity_score_df


def matched_simulation_experiment_uncorrected(run,
                                              NN_architecture,
                                              analysis_name,
                                              num_simulated_samples,
                                              lst_num_partitions,
                                              corrected,
                                              use_pca,
                                              num_PCs,
                                              file_prefix,
                                              input_file):

  local_dir = "/home/alexandra/Documents/"

  # Main

  # Generate simulated data
  simulated_data = generate_data_parallel.simulate_compendium(num_simulated_experiments,
                                                              input_file,
                                                              NN_architecture,
                                                              analysis_name)

  # Permute simulated data to be used as a negative control
  permuted_data = generate_data_parallel.permute_data(simulated_data,
                                                      local_dir,
                                                      analysis_name)

  # Add technical variation
  generate_data_parallel.add_experiments_grped_io(simulated_data,
                                                  lst_num_partitions,
                                                  run,
                                                  local_dir,
                                                  analysis_name)

 # Calculate similarity between compendium and compendium + noise
  batch_scores, permuted_score = similarity_metric_parallel.sim_svcca_io(simulated_data,
                                                                         permuted_data,
                                                                         corrected,
                                                                         file_prefix,
                                                                         run,
                                                                         lst_num_partitions,
                                                                         use_pca,
                                                                         num_PCs,
                                                                         local_dir,
                                                                         analysis_name)

  # Convert similarity scores to pandas dataframe
  similarity_score_df = pd.DataFrame(data={'score': batch_scores},
                                     index=lst_num_partitions,
                                     columns=['score'])

  similarity_score_df.index.name = 'number of partitions'
  similarity_score_df

  # Return similarity scores and permuted score
  return permuted_score, similarity_score_df


def simple_simulation_experiment_corrected(run,
                                           NN_architecture,
                                           analysis_name,
                                           num_simulated_samples,
                                           lst_num_experiments,
                                           corrected,
                                           use_pca,
                                           num_PCs,
                                           file_prefix,
                                           input_file):

  local_dir = "/home/alexandra/Documents/"

  # Main

  # Generate simulated data
  simulated_data = generate_data_parallel.simulate_data(input_file,
                                                        NN_architecture,
                                                        analysis_name,
                                                        num_simulated_samples
                                                        )

  # Permute simulated data to be used as a negative control
  permuted_data = generate_data_parallel.permute_data(simulated_data,
                                                      local_dir,
                                                      analysis_name)

  # Add technical variation
  generate_data_parallel.add_experiments_io(simulated_data,
                                            lst_num_experiments,
                                            run,
                                            local_dir,
                                            analysis_name)

  # Remove technical variation
  generate_data_parallel.apply_correction_io(local_dir,
                                             run,
                                             analysis_name,
                                             lst_num_experiments)

  # Calculate similarity between compendium and compendium + noise
  batch_scores, permuted_score = similarity_metric_parallel.sim_svcca_io(simulated_data,
                                                                         permuted_data,
                                                                         corrected,
                                                                         file_prefix,
                                                                         run,
                                                                         lst_num_experiments,
                                                                         use_pca,
                                                                         num_PCs,
                                                                         local_dir,
                                                                         analysis_name)

  # batch_scores, permuted_score

  # Convert similarity scores to pandas dataframe
  similarity_score_df = pd.DataFrame(data={'score': batch_scores},
                                     index=lst_num_experiments,
                                     columns=['score'])

  similarity_score_df.index.name = 'number of experiments'
  similarity_score_df

  # Return similarity scores and permuted score
  return permuted_score, similarity_score_df


def matched_simulation_experiment_corrected(run,
                                            NN_architecture,
                                            analysis_name,
                                            num_simulated_samples,
                                            lst_num_partitions,
                                            corrected,
                                            use_pca,
                                            num_PCs,
                                            file_prefix,
                                            input_file):

  local_dir = "/home/alexandra/Documents/"

  # Main

  # Generate simulated data
  simulated_data = generate_data_parallel.simulate_compendium(num_simulated_experiments,
                                                              input_file,
                                                              NN_architecture,
                                                              analysis_name)

  # Permute simulated data to be used as a negative control
  permuted_data = generate_data_parallel.permute_data(simulated_data,
                                                      local_dir,
                                                      analysis_name)

  # Add technical variation
  generate_data_parallel.add_experiments_grped_io(simulated_data,
                                                  lst_num_partitions,
                                                  run,
                                                  local_dir,
                                                  analysis_name)

  # Remove technical variation
  generate_data_parallel.apply_correction_io(local_dir,
                                             run,
                                             analysis_name,
                                             lst_num_partitions)

  # Calculate similarity between compendium and compendium + noise
  batch_scores, permuted_score = similarity_metric_parallel.sim_svcca_io(simulated_data,
                                                                         permuted_data,
                                                                         corrected,
                                                                         file_prefix,
                                                                         run,
                                                                         lst_num_partitions,
                                                                         use_pca,
                                                                         num_PCs,
                                                                         local_dir,
                                                                         analysis_name)

  # batch_scores, permuted_score

  # Convert similarity scores to pandas dataframe
  similarity_score_df = pd.DataFrame(data={'score': batch_scores},
                                     index=lst_num_partitions,
                                     columns=['score'])

  similarity_score_df.index.name = 'number of partitions'
  similarity_score_df

  # Return similarity scores and permuted score
  return permuted_score, similarity_score_df
