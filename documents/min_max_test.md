# Dominance Test

## Why do we need this?
When ANOVA has significant findings, it does not report which means are different. This test quantifies the probability that the observed difference on mean —for the highest and lowest performing groups— could have been observed by random chance alone relative to their closest competitors.

This test is designed for **one-to-many comparisons**. It compares a specific target group against all other groups to determine if it maintains a statistically significant lead over even its nearest rival.

## Theoretical Background

This test is built on a variation of [Dunnett's Test](https://en.wikipedia.org/wiki/Dunnett%27s_test) called **"Global Dominance"** or the **Min-Test** (see [Dunnett & Tamhane, 1992](https://doi.org/10.2307/2531766)).

**What's the difference?**

- **Standard Dunnett's Test**: Uses a many-to-one comparison logic, where a control group is compared against all other groups individually.
- **Min-Test (our approach)**: Designed specifically to prove **dominance**. Instead of testing each comparison separately, we focus on the toughest competitor—the one closest to our target group.

### The Key Insight: "The Weakest Link"

Think of it this way: if you want to prove you're the fastest runner in your class, you don't just need to beat the slowest person—you need to beat **everyone**, including the second-fastest runner. Your victory is only as strong as your narrowest margin.

In statistical terms, when we claim that **Process 1 is the best**, we're really saying:

$$H_1: \text{Mean}(P1) > \text{Mean}(P2) \text{ and } \text{Mean}(P1) > \text{Mean}(P3)$$

The test asks: **"What's your smallest advantage?"** Because if even that smallest gap is statistically significant, all your other advantages must be significant too.

## A Real-World Example: Fabric Strength

Let's use the classic *Breaking Strength of Fabric* example from Wikipedia's Dunnett's Test page to see this in action.

Imagine a textile factory testing 4 different manufacturing processes:
- **Process 1 (P1)**: New experimental method
- **Process 2 (P2)**: Alternative method
- **Process 3 (P3)**: Another variation
- **Standard (S)**: Current production method

After testing, we find:
- Mean(P1) = 50 (best)
- Mean(P2) = 41
- Mean(P3) = 45
- Mean(S) = 42

**The Question**: Is Process 1 truly superior, or could this just be random variation?

**Our Practical Approach**:

1. Calculate the **minimum difference** for P1 against all competitors:
   ```
   min(P1 - P2, P1 - P3) = min(9, 5) = 5
   ```

2. This tells us: **P1's toughest competitor is P3, with only a 5-point gap.**

3. Now we shuffle the data randomly thousands of times and ask:
   > "If there were no real differences between processes, how often would random chance alone produce a minimum gap of 5 or more?"

4. **If 95% of random simulations produce gaps smaller than 5**, then we conclude:
   - There's less than a 5% chance this 5-point advantage is due to luck
   - P1 is statistically dominant (p < 0.05)
   - Since it beats even its closest rival, it beats everyone!

**The Bottom Line**: You're a chain, and your strength is determined by your weakest link. This test checks if even your weakest link is strong enough.
