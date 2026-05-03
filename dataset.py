"""Generate synthetic time series data for statistical testing demonstrations."""

import numpy as np
import pandas as pd

# Constants
RANDOM_SEED = 42
SAMPLES_PER_MONTH = 100
NUM_MONTHS = 12
BASE_VALUE = 0.4
STANDARD_VARIANCE = 0.2
LOW_VARIANCE = 0.05
TREND_SLOPE = 1 / 50  # Increase per month
SEASONAL_AMPLITUDE = 0.3
STEP_INCREASE = 0.4
STEP_MONTH = 6
NUM_OUTLIERS = 10
OUTLIER_MULTIPLIER = 5

# Column names
GROUP_COL = "moy"  # Month of year
VALUE_COL = "m3"  # Cubic meters
DISTRICT_COL = "district"


def _create_district_dataframe(
    district_name: str, months: np.ndarray, values: np.ndarray
) -> pd.DataFrame:
    """Create a DataFrame for a single district with standard column names.

    Args:
        district_name: Name identifier for the district (e.g., 'A', 'B')
        months: Array of month values (1-12, repeated)
        values: Array of measurement values

    Returns:
        DataFrame with district, month, and value columns
    """
    return pd.DataFrame({DISTRICT_COL: district_name, GROUP_COL: months, VALUE_COL: values})


def _generate_positive_trend(months: np.ndarray) -> np.ndarray:
    """Generate data with a clear upward trend and low variance.

    District A: Used to test trend detection algorithms.

    Args:
        months: Array of month values

    Returns:
        Array of values showing positive trend
    """
    base_noise = np.abs(np.random.normal(loc=BASE_VALUE, scale=LOW_VARIANCE, size=len(months)))
    trend_component = np.repeat(range(1, NUM_MONTHS + 1), SAMPLES_PER_MONTH) * TREND_SLOPE
    return base_noise + trend_component


def _generate_no_trend(months: np.ndarray) -> np.ndarray:
    """Generate data with no trend, just random noise.

    District B: Control group for testing that null hypothesis is not rejected when true.

    Args:
        months: Array of month values

    Returns:
        Array of values with no trend
    """
    return np.abs(np.random.normal(loc=BASE_VALUE, scale=STANDARD_VARIANCE, size=len(months)))


def _generate_seasonal_pattern(months: np.ndarray) -> np.ndarray:
    """Generate data with cyclical seasonal pattern but no overall trend.

    District C: Tests ability to distinguish seasonality from trends.
    Pattern follows a sine wave that starts at 0 and ends at 0 (full cycle).

    Args:
        months: Array of month values

    Returns:
        Array of values with seasonal variation
    """
    base_noise = np.abs(np.random.normal(loc=BASE_VALUE, scale=STANDARD_VARIANCE, size=len(months)))
    seasonal_component = np.sin(np.linspace(0, 2 * np.pi, len(months))) * SEASONAL_AMPLITUDE
    return base_noise + seasonal_component


def _generate_step_change(months: np.ndarray) -> np.ndarray:
    """Generate data with a sudden level shift (step function) but no trend.

    District D: Tests ability to distinguish step changes from gradual trends.
    Values increase by a fixed amount after month 6.

    Args:
        months: Array of month values

    Returns:
        Array of values with step change at midpoint
    """
    base_noise = np.abs(np.random.normal(loc=BASE_VALUE, scale=STANDARD_VARIANCE, size=len(months)))
    step_component = np.where(months > STEP_MONTH, STEP_INCREASE, 0.0)
    return base_noise + step_component


def _generate_with_outliers(months: np.ndarray) -> np.ndarray:
    """Generate data with extreme outliers but no underlying trend.

    District E: Tests robustness of algorithms to outliers.
    Random observations are multiplied by 5x to create extreme values.

    Args:
        months: Array of month values

    Returns:
        Array of values with random outliers
    """
    values = np.abs(np.random.normal(loc=BASE_VALUE, scale=STANDARD_VARIANCE, size=len(months)))
    outlier_indices = np.random.choice(len(months), NUM_OUTLIERS, replace=False)
    values[outlier_indices] *= OUTLIER_MULTIPLIER
    return values


def make_time_series_data() -> pd.DataFrame:
    """Generate synthetic time series data for 5 districts with different patterns.

    Creates monthly water consumption data (m3) for testing statistical methods:
    - District A: Clear positive trend (for trend detection)
    - District B: No trend (null hypothesis control)
    - District C: Seasonal pattern (distinguish from trends)
    - District D: Step change (distinguish from gradual trends)
    - District E: Outliers (test robustness)

    Each district has 100 observations per month across 12 months (1,200 total per district).

    Returns:
        DataFrame with columns: district, moy (month), m3 (consumption)
        Total rows: 6,000 (5 districts * 1,200 observations)

    Example:
        >>> df = make_time_series_data()
        >>> df.groupby('district')['m3'].agg(['mean', 'std'])
    """
    np.random.seed(RANDOM_SEED)

    # Create month array: [1,1,1,...,2,2,2,...,12,12,12] (100 samples per month)
    months = np.repeat(np.arange(1, NUM_MONTHS + 1), SAMPLES_PER_MONTH)

    # Generate data for each district with distinct patterns
    districts = [
        ("A", _generate_positive_trend(months)),
        ("B", _generate_no_trend(months)),
        ("C", _generate_seasonal_pattern(months)),
        ("D", _generate_step_change(months)),
        ("E", _generate_with_outliers(months)),
    ]

    # Create DataFrames for each district and combine
    dataframes = [_create_district_dataframe(name, months, values) for name, values in districts]

    return pd.concat(dataframes, ignore_index=True)
