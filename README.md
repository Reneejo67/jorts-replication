# Replication Materials for *Emergent structures of attention on social media are driven by amplification and triad transitivity*

## Project Abstract
As they evolve, social networks tend to form transitive triads more often than random chance and structural constraints would suggest. However, the mechanisms by which triads in these networks become transitive are largely unexplored.  We leverage a unique combination of data and methods to demonstrate a causal link between amplification and triad transitivity in a directed social network. Additionally, we develop the concept of the "attention broker," an extension of the previously theorized tertius iungens (or "third who joins"). We use a novel technique to identify time-bounded Twitter/X following events, and then use difference-in-differences to show that attention brokers cause triad transitivity by amplifying content. Attention brokers intervene in the evolution of any sociotechnical system where individuals can amplify content while referencing its originator.

The full dataset consists of the time-bounded follower counts, and their associated timings, for each retweeted account and attention broker followers and non-followers. All retweeted accounts' usernames and followers' user IDs are hashed using a non-reversible hash function for privacy.

## Contents (code)
- `{jkr, jorts}_data_parsing_interpolation_clean.ipynb`: iPython notebooks containing the data parsing and interpolation functionality for each attention broker case. Each notebook also includes a pre-trends analysis and produces the .tsv of data required for the differences-in-differences event study.
- `{jkr, jorts}_population_estimate_data_prep.ipynb`: iPython notebooks containing data parsing functionality to construct .txt files of mark/recapture events in a suitable format for Project MARK R software to use. We use Project MARK to obtain estimates of the "eligible follower" and "eligible non-follower" populations using the Jolly-Seber mark-recapture population estimator. 
- `jorts_utils.py`: Python file containing utility functions for data parsing and interpolation.
- `mark_estimation.R`: R file that runs the POPAN implementation of the Jolly-Seber mark-recapture population estimator. 
- `{jkr, jorts}_did.R`: R file that runs the differences-in-differences event studies for each attention broker case and plots the results.
- `triad_closure.py`: Python script demonstrating the time-bounded following event collection procedure

## Data:
The replication data can be accessed at SOMAR (the Social Media Archive at ICPSR) [here](https://socialmediaarchive.org/record/65). 

You can cite it as follows:

Smith, Alyssa, Green, Jonathan, Foucault Welles, Brooke, and Lazer, David. Replication data for "Emergent structures of attention on social media are driven by amplification and triad transitivity." Inter-university Consortium for Political and Social Research [distributor], 2025-03-28. https://doi.org/10.3886/3swn-td91

For best results, place the data in a directory at this level labeled `data`.
- `all_{jkr, jorts}_did_data_test_all.tsv`: TSV containing the interpolated per-account per-day follower accumulation for known followers & non-followers of each attention broker.
- `HASHED_jkr_followers_full_past_20180615.json`: json object mapping all of J.K. Rowling's followers accumulated after June 15, 2018 to a cursor timestamp bounding the time at which the following event occurred. Each follower's user ID is hashed using SHA256 for privacy.
- `HASHED_jorts_follower_data_by_cursor_all.json`: json object mapping all of Jorts the Cat's followers accumulated during the period of study to a cursor timestamp bounding the time at which the following event occurred. Each follower's user ID is hashed using SHA256 for privacy. 
- `HASHED_jkr_rts_labels_final.tsv`: TSV file containing the coded labels for all accounts retweeted by J.K. Rowling in the period of study
- `HASHED_jkr_rts_past_20180615.tsv`: TSV file containing all of J.K. Rowling's retweets for the period of study
- `HASHED_jorts_ground_truth_full.json`: json object indicating union assocation for each of Jorts the Cat's retweeted accounts 
- `HASHED_jorts_rt_authors_to_ts.json`: json object mapping authors retweeted by Jorts the Cat to the timestamps at which the retweets occurred.
- `{jkr, jorts}/HASHED_*.json`: json object mapping cursor timestamps bounding follow timings to lists of hashed user IDs of followers. 
