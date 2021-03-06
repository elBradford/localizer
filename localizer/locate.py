import numpy as np
import pandas as pd


def locate_naive(series):
    if len(series) > 360:
        series = series[np.arange(0, 360)]

    return series.idxmax()


def locate_interpolate(series_concat, method):
    series_inter = series_concat.interpolate(method=method)[np.arange(0, 360)]

    return series_inter.idxmax()


def prep_for_interpolation(dataframe, bearing, x='bearing_magnetic', y='mw'):
    """
    Prepare a dataframe for interpolation by stripping extraneous columns and converting it into a series
    """

    # Stip columns and convert to series
    df = dataframe.filter([x, y]).rename(columns={x: 'deg'}).sort_values('deg')
    df['deg'] = np.round(df['deg'])

    if df.duplicated('deg', keep=False).any():
        df = df.groupby('deg', group_keys=False).apply(lambda z: z.loc[z.mw.idxmax()])

    series_mid = df.set_index('deg').reindex(np.arange(0, 360)).iloc[:, 0]

    if bearing >= 360:
        # Extend to the left and right in order to ease interpolation
        series_left = series_mid.copy()
        series_left.index = np.arange(-360, 0)
        series_right = series_mid.copy()
        series_right.index = np.arange(360, 720)

        series_concat = pd.concat([series_left, series_mid, series_right])

        return series_concat
    else:
        return series_mid


def interpolate(series, bearing):
    """
    Interpolate the given series in the best manner based on testing
    :param series: Pandas Series
    :param expand_to_360: Whether to expand series so that it properly wraps around 360 degrees
    :return:
    """

    if 0 > len(series) <= 1:
        _method = 'slinear'
    elif 1 > len(series) <= 2:
        _method = 'naive'
    else:
        _method = 'pchip'

    _guess = _error_methods[_method](prep_for_interpolation(series, bearing))
    return _guess, _method


_error_methods = {
    'naive': locate_naive,
    'quadratic': lambda series: locate_interpolate(series, 'quadratic'),
    'cubic': lambda series: locate_interpolate(series, 'cubic'),
    'linear': lambda series: locate_interpolate(series, 'linear'),
    'slinear': lambda series: locate_interpolate(series, 'slinear'),
    'barycentric': lambda series: locate_interpolate(series, 'barycentric'),
    'krogh': lambda series: locate_interpolate(series, 'krogh'),
    'piecewise_polynomial': lambda series: locate_interpolate(series, 'piecewise_polynomial'),
    'from_derivatives': lambda series: locate_interpolate(series, 'from_derivatives'),
    'pchip': lambda series: locate_interpolate(series, 'pchip'),
    'akima': lambda series: locate_interpolate(series, 'akima'),
}
