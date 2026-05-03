# 🎲 Thinking in Numbers

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-enabled-green.svg)](https://github.com/astral-sh/uv)
[![Streamlit](https://img.shields.io/badge/streamlit-interactive-red.svg)](https://streamlit.io/)

> **Learn statistics from first principles through interactive simulation and visualization.**

Stop memorizing formulas. Start building intuition. This project teaches statistics the way it should be taught—by letting you **see** and **play with** the concepts through interactive apps, not just read about them.

---

## 🎯 What This Is

An **interactive statistics method** that takes you from zero to understanding:
- How to describe and visualize data
- Why the Central Limit Theorem is magical
- How hypothesis testing actually works (via simulation, not formulas)
- Time series patterns and clustering techniques

**Learn by doing**: Every concept has an interactive Streamlit app where you adjust parameters, see results instantly, and build genuine intuition.

**Built with modern tools**: Uses `uv` for fast dependency management and includes both Python and BigQuery SQL examples for scale.

---

## 🚀 Quick Start

```bash
# Install dependencies (we recommend uv—10-100x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv first (or: pip install uv)

# Setup project
git clone <your-repo-url>
cd thinking-in-numbers
uv sync

# Launch app
uv run streamlit run main.py
```

<details>
<summary>Using pip? Click here</summary>

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run main.py
```
</details>

**📚 Learning Path** (follow this order):

1️⃣ Estimates of Location → 2️⃣ Variability → 3️⃣ Distributions → 4️⃣ Central Limit Theorem → 5️⃣ Permutation Tests → 6️⃣ Time Series → 7️⃣ Clustering

Use the sidebar in the app to navigate between sections.

---

## 📖 What You'll Learn

### 1️⃣ **Estimates of Location**
Where is the "center"? Compare mean, median, trimmed mean, weighted mean on real data.

**Launch**: `main.py` → Select "Estimates of Location" | **Files**: [`estimates_of_location.py`](estimates_of_location.py)

---

### 2️⃣ **Estimates of Variability**
How spread out? Learn range, variance, standard deviation, IQR, MAD. Understand population vs sample (n vs n-1).

**Launch**: `main.py` → Select "Estimates of Variability" | **Files**: [`estimates_of_variability.py`](estimates_of_variability.py)

---

### 3️⃣ **Exploring Data Distributions**
See the shape. Histograms, boxplots, Q-Q plots, frequency tables. Check if data is normal, skewed, or bimodal.

**Launch**: `main.py` → Select "Exploring the Data Distribution" | **Files**: [`data_distribution.py`](data_distribution.py)

---

### 4️⃣ **Central Limit Theorem**
The magic: Sample means are **always normal**, even if your data isn't. This is why hypothesis testing works.

**Try it**: Sample from exponential, uniform, Poisson, etc. Watch the means form a bell curve every time.

**Launch**: `main.py` → Select "Central Limit" | **Files**: [`theorem.py`](theorem.py)

---

### 5️⃣ **Permutation Tests & Hypothesis Testing**
Test hypotheses through simulation: shuffle data thousands of times, count how often random chance beats your observation. No formulas, just counting.

**Main app**: `main.py` → Select "Permutation"

**Specialized tests** (run with `perm.py`):
- **5.1 t-test**: Is Page B better than Page A? ([`t_test.py`](t_test.py))
- **5.2 Conversion Rate**: Did pricing change matter? ([`conv_rate.py`](conv_rate.py))
- **5.3 ANOVA**: Do groups differ? ([`anova.py`](anova.py))
- **5.4 Dominance Test**: Is the winner definitively best? → [Detailed docs](documents/min_max_test.md) | ([`min_max.py`](min_max.py))
- **5.5 Trend Test**: Real trend or noise? → [Detailed docs](documents/trend_test.md) | ([`trend.py`](trend.py))

**Launch specialized tests**: `uv run streamlit run perm.py`

---

### 6️⃣ **Time Series**
Trends, seasonality, moving averages, anomaly detection for temporal data.

**Launch**: `main.py` → Select "Timeseries" | **Files**: [`ts.py`](ts.py), [`bq-ts.sql`](bq-ts.sql)

---

### 7️⃣ **Clustering**
Find natural groupings. K-means and hierarchical clustering. Choose K, visualize clusters, measure quality.

**Launch**: `main.py` → Select "Cluster" | **Files**: [`cluster.py`](cluster.py), [`bq-kmeans.sql`](bq-kmeans.sql)

---

## 🗄️ BigQuery & SQL

For large datasets (millions of rows), use SQL implementations:
- **[`bq-kmeans.sql`](bq-kmeans.sql)**: K-means clustering at scale
- **[`bq-ts.sql`](bq-ts.sql)**: Time series analysis in SQL
- **[`ml-bq-linear-regression.sql`](ml-bq-linear-regression.sql)**: BigQuery ML regression
- **[`bq.py`](bq.py)**: Python-BigQuery integration

```python
from bq import run_sql
results = run_sql("SELECT district, AVG(consumption) FROM water_data GROUP BY district")
```

---

## 🎯 Who Is This For?

✅ **Students** learning statistics
✅ **Data Analysts** explaining tests to stakeholders
✅ **Practitioners** wanting to understand what their tools actually do
✅ **Educators** looking for interactive teaching materials

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-test`)
3. Commit your changes
4. Push and open a Pull Request

---

## 📖 Further Reading

- [Permutation Tests](https://en.wikipedia.org/wiki/Permutation_test)
- [Dunnett's Test](https://en.wikipedia.org/wiki/Dunnett%27s_test) (basis for dominance test)
- [Resampling Methods](https://en.wikipedia.org/wiki/Resampling_(statistics))

---

## 💡 Philosophy

> "The best way to understand a statistical test is to **build it from scratch**."

- 🎲 Simulation beats formula memorization
- 🔍 Seeing beats believing
- 🧩 Building beats consuming
- 💬 Intuition beats jargon

**Statistics doesn't have to be mysterious. Let's make it transparent.**

---

⭐ **If this helped you understand statistics better, give it a star!**

**Questions?** Open an issue or find me on [LinkedIn](https://www.linkedin.com/in/h%C3%BCsn%C3%BC-%C5%9Fensoy-3a406313/).
