# Dominance Test

## Why do we need this?
When ANOVA has significant findings, it does not report which means are different. This test quantifies the probability that the observed difference on mean —for the highest and lowest performing groups— could have been observed by random chance alone relative to their closest competitors.

This test is designed for **one-to-many comparisons**. It compares a specific target group against all other groups to determine if it maintains a statistically significant lead over even its nearest rival.

## How does it work?

**Difference Matrix:**

+ We calculate the observed mean value for each group. Then, we construct a pairwise difference matrix and replace diagonal with **np.nan** to avoid self-comparison

```python
obs_means = df.groupby(group_col)[value_col].mean().sort_index()
keys, values = obs_means.index, obs_means.values
diff_matrix = values[:, None] - values

np.fill_diagonal(diff_matrix, np.nan)
```
**Observations and Test Type:**

+ For testing Highest mean (`type` = *greater*), we look for the mininmum difference across pairwise groups. Logic: group with highest mean must be significantly higher than even the second-best group. If it beats the closest rival, it beats every group.

+ For testing Lowest mean (`type` = *lesser*), we look for the maximum difference across pairwise groups. Since the differences are negative, the maximum value is the one closest to zero. This represents the gap between the closest rival.

+ We filter the results to focus only on the groups in the `control_groups` list. Why a list? Although the test is designed for **one-to-many** comparison. the list argument allows us to screen multiple groups iteratively for exploratory purposes. We expect only one group to return a significant p-value. Testing other groups to confirm they do not share this dominance.

```python
if type == "greater":
        results = np.nanmin(diff_matrix, axis=1)
    elif type == "lesser":
        results = np.nanmax(diff_matrix, axis=1)

    control_groups.sort()
    result_map = dict(zip(keys, results))
    control_maps = {k: result_map[k] for k in control_groups}
```
**Permuation Difference Function:**

Now, we are going to quantify whether these observed worst-case differences are random. We create a permutation function to permute observations in our future simulations.

+ First, we shuffle indices with `np.random.permutation(len(df))`. Then, we create `mean_dict` to store mean of permuted groups.

```python
shuffled_indices = np.random.permutation(len(df))
        start = 0
        mean_dict = {}
        for i, n in enumerate(df[group_col].value_counts().sort_index()):
            idx = shuffled_indices[start : start + n]
            mean = df[value_col].loc[idx].mean()
            start += n
            mean_dict[keys[i]] = mean
        perm_results = {}
```
__If `type` = *greater:*__

+ we calculate pairwise differences between the target group (variable name of the target group is `control`) and all other groups, return the minimum difference to measure the margin against the closest competitor.

```python
if type == "greater":
    for control in control_maps:
        c_mean = mean_dict[control]
        min_diff = +np.inf
        for group, g_mean in mean_dict.items():
            if group != control:
                diff = c_mean - g_mean
                if diff < min_diff:
                    min_diff = diff
        if min_diff < +np.inf:
            perm_results[control] = min_diff
    return perm_results

```
__If `type` = *lesser:*__

+ we apply similar logic above to return the maximum difference to measure the margin against the closest competitor.

```python
elif type == "lesser":
    for control in control_maps:
        c_mean = mean_dict[control]
        max_diff = -np.inf
        for group, g_mean in mean_dict.items():
            if group != control:
                diff = c_mean - g_mean
                if diff > max_diff:
                    max_diff = diff
        if max_diff > -np.inf:
            perm_results[control] = max_diff
    return perm_results
```

**Final Part - Simulation and P-Value Calculation:**

+ Finally, we generate a distribution (`results`) by running the permutation function `iterations` times

+ We calculate the proportion of simulated scenarios where the random difference was more extreme than our observed difference.

+ For `type` = _greater_, how often did random noise produce a higher peak than our observation?
+ For `type` = _lesser_, how often did random noise produce a lower dip than our observation?

```python
results = pd.DataFrame([perm_diff() for _ in range(iterations)])
    p_values = (
        (results > control_maps).mean()
        if type == "greater"
        else (results < control_maps).mean()
    )
    return results, p_values, control_maps
```
