from __future__ import division, unicode_literals
import warnings

import numpy as np

import matplotlib.cm as cm
import matplotlib.pyplot as pl
import matplotlib

from plots.colors import *
from plots._labels import labels
from plots._utils import convert_to_link, LogitLink

def decision_plot_matplotlib(
    base_values,
    cumsum,
    ascending,
    feature_display_count,
    features,
    feature_names,
    highlight,
    plot_color,
    axis_color,
    y_demarc_color,
    xlim,
    alpha,
    color_bar,
    auto_size_plot,
    title,
    show,
    legend_labels,
    legend_location,
    link_logit
):
    """matplotlib rendering for decision_plot()"""

    # image size
    row_height = 0.4
    if auto_size_plot:
        pl.gcf().set_size_inches(8, feature_display_count * row_height + 1.5)

    # draw vertical line indicating decision boundary
    if link_logit:
        pl.axvline(x=0.5, color="#999999", zorder=-1)
    else:
        pl.axvline(x=0, color="#999999", zorder=-1)

    # draw horizontal dashed lines for each feature contribution
    for i in range(1, feature_display_count):
        pl.axhline(y=i, color=y_demarc_color, lw=0.5, dashes=(1, 5), zorder=-1)

    # initialize highlighting
    linestyle = np.array("-", dtype=np.object)
    linestyle = np.repeat(linestyle, cumsum.shape[0])
    linewidth = np.repeat(1, cumsum.shape[0])
    if highlight is not None:
        linestyle[highlight] = "-."
        linewidth[highlight] = 2

    # plot each observation's cumulative SHAP values.
    ax = pl.gca()
    ax.set_xlim(xlim)
    m = cm.ScalarMappable(cmap=plot_color)
    m.set_clim(xlim)
    y_pos = np.arange(0, feature_display_count + 1)
    lines = []
#     line_colors = ['r', 'b', 'g']
    line_color_map = pl.cm.Set1(np.linspace(0, 1, 12))
    line_colors = line_color_map[2:cumsum.shape[0]+2]
    for i in range(cumsum.shape[0]):
        o = pl.plot(
            cumsum[i, :],
            y_pos,
#             color=m.to_rgba(cumsum[i, -1], alpha),
            color = line_colors[i],
            linewidth=linewidth[i],
            linestyle=linestyle[i]
        )
        lines.append(o[0])
    # determine font size. if ' *\n' character sequence is found (as in interaction labels), use a smaller
    # font. we don't shrink the font for all interaction plots because if an interaction term is not
    # in the display window there is no need to shrink the font.
    s = next((s for s in feature_names if " *\n" in s), None)
    fontsize = 13 if s is None else 9

    # if there is a single observation and feature values are supplied, print them.
    if (cumsum.shape[0] == 1) and (features is not None):
        renderer = pl.gcf().canvas.get_renderer()
        inverter = pl.gca().transData.inverted()
        y_pos = y_pos + 0.5
        for i in range(feature_display_count):
            v = features[0, i]
            if isinstance(v, str):
                v = "({})".format(str(v).strip())
            else:
                v = "({})".format("{0:,.3f}".format(v).rstrip("0").rstrip("."))
            t = ax.text(np.max(cumsum[0, i:(i + 2)]), y_pos[i], "  " + v, fontsize=fontsize,
                    horizontalalignment="left", verticalalignment="center_baseline", color="#666666")
            bb = inverter.transform_bbox(t.get_window_extent(renderer=renderer))
            if bb.xmax > xlim[1]:
                t.set_text(v + "  ")
                t.set_x(np.min(cumsum[0, i:(i + 2)]))
                t.set_horizontalalignment("right")
                bb = inverter.transform_bbox(t.get_window_extent(renderer=renderer))
                if bb.xmin < xlim[0]:
                    t.set_text(v)
                    t.set_x(xlim[0])
                    t.set_horizontalalignment("left")

    # style axes
    ax.xaxis.set_ticks_position("both")
    ax.yaxis.set_ticks_position("none")
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(color=axis_color, labelcolor=axis_color, labeltop=True)
    pl.yticks(np.arange(feature_display_count) + 0.5, feature_names, fontsize=fontsize)
    ax.tick_params("x", labelsize=11)
    pl.ylim(0, feature_display_count)
    pl.xlabel(labels["MODEL_OUTPUT"], fontsize=13)

    # draw the color bar - must come after axes styling
    if color_bar:
        m = cm.ScalarMappable(cmap=plot_color)
        m.set_array(np.array([0, 1]))

        # place the colorbar
        pl.ylim(0, feature_display_count + 0.25)
        ax_cb = ax.inset_axes([xlim[0], feature_display_count, xlim[1] - xlim[0], 0.25], transform=ax.transData)
        cb = pl.colorbar(m, ticks=[0, 1], orientation="horizontal", cax=ax_cb)
        cb.set_ticklabels([])
        cb.ax.tick_params(labelsize=11, length=0)
        cb.set_alpha(alpha)
        cb.outline.set_visible(False)

        # re-activate the main axis for drawing.
        pl.sca(ax)

    if title:
        # TODO decide on style/size
        pl.title(title)

    if ascending:
        pl.gca().invert_yaxis()

    if legend_labels is not None:
        ax.legend(handles=lines, labels=legend_labels, loc=legend_location)

    if show:
        pl.show()
def decision(
    base_values,
    shap_values,
    features=None,
    feature_names=None,
    feature_order="importance",
    feature_display_range=None,
    highlight=None,
    link="identity",
    plot_color=None,
    axis_color="#333333",
    y_demarc_color="#333333",
    alpha=None,
    color_bar=True,
    auto_size_plot=True,
    title=None,
    xlim=None,
    show=True,
    return_objects=False,
    ignore_warnings=False,
    new_base_value=None,
    legend_labels=None,
    legend_location="best",
    link_logit=False
):
    """Visualize model decisions using cumulative SHAP values.
    Each plotted line explains a single model prediction. If a single prediction is plotted, feature values will be
    printed in the plot (if supplied). If multiple predictions are plotted together, feature values will not be printed.
    Plotting too many predictions together will make the plot unintelligible.
    Parameters
    ----------
    base_value : float or numpy.ndarray
        This is the reference value that the feature contributions start from. Usually, this is
        explainer.expected_value.
    shap_values : numpy.ndarray
        Matrix of SHAP values (# features) or (# samples x # features) from explainer.shap_values(). Or cube of SHAP
        interaction values (# samples x # features x # features) from explainer.shap_interaction_values().
    features : numpy.array or pandas.Series or pandas.DataFrame or numpy.ndarray or list
        Matrix of feature values (# features) or (# samples x # features). This provides the values of all the
        features and, optionally, the feature names.
    feature_names : list or numpy.ndarray
        List of feature names (# features). If None, names may be derived from the features argument if a Pandas
        object is provided. Otherwise, numeric feature names will be generated.
    feature_order : str or None or list or numpy.ndarray
        Any of "importance" (the default), "hclust" (hierarchical clustering), "none", or a list/array of indices.
    feature_display_range: slice or range
        The slice or range of features to plot after ordering features by feature_order. A step of 1 or None
        will display the features in ascending order. A step of -1 will display the features in descending order. If
        feature_display_range=None, slice(-1, -21, -1) is used (i.e. show the last 20 features in descending order).
        If shap_values contains interaction values, the number of features is automatically expanded to include all
        possible interactions: N(N + 1)/2 where N = shap_values.shape[1].
    highlight : Any
        Specify which observations to draw in a different line style. All numpy indexing methods are supported. For
        example, list of integer indices, or a bool array.
    link : str
        Use "identity" or "logit" to specify the transformation used for the x-axis. The "logit" link transforms
        log-odds into probabilities.
    plot_color : str or matplotlib.colors.ColorMap
        Color spectrum used to draw the plot lines. If str, a registered matplotlib color name is assumed.
    axis_color : str or int
        Color used to draw plot axes.
        
    y_demarc_color : str or int
        Color used to draw feature demarcation lines on the y-axis.
        
    alpha : float
        Alpha blending value in [0, 1] used to draw plot lines.
        
    color_bar : bool
        Whether to draw the color bar.
        
    auto_size_plot : bool
        Whether to automatically size the matplotlib plot to fit the number of features displayed. If `False`, 
        specify the plot size using matplotlib before calling this function.
        
    title : str
        Title of the plot.
        
    xlim: tuple[float, float]
        The extents of the x-axis (e.g. (-1.0, 1.0)). If not specified, the limits are determined by the
        maximum/minimum predictions centered around base_value when link='identity'. When link='logit', the
        x-axis extents are (0, 1) centered at 0.5. x_lim values are not transformed by the link function. This
        argument is provided to simplify producing multiple plots on the same scale for comparison.
    show : bool
        Whether to automatically display the plot.
    return_objects : bool
        Whether to return a DecisionPlotResult object containing various plotting features. This can be used to
        generate multiple decision plots using the same feature ordering and scale.
        
    ignore_warnings : bool
        Plotting many data points or too many features at a time may be slow, or may create very large plots. Set
        this argument to `True` to override hard-coded limits that prevent plotting large amounts of data.
    new_base_value : float
        SHAP values are relative to a base value; by default, the expected value of the model's raw predictions. Use
        `new_base_value` to shift the base value to an arbitrary value (e.g. the cutoff point for a binary
        classification task).
    legend_labels : list of str
        List of legend labels. If `None`, legend will not be shown.
    legend_location : str
        Legend location. Any of "best", "upper right", "upper left", "lower left", "lower right", "right",
        "center left", "center right", "lower center", "upper center", "center".
    Returns
    -------
    Returns a DecisionPlotResult object if `return_objects=True`. Returns `None` otherwise (the default).
    Example
    -------
    Plot two decision plots using the same feature order and x-axis.
        >>> range1, range2 = range(20), range(20, 40)
        >>> r = decision_plot(base, shap_values[range1], features[range1], return_objects=True)
        >>> decision_plot(base, shap_values[range2], features[range2], feature_order=r.feature_idx, xlim=r.xlim)
    """

    # code taken from force_plot. auto unwrap the base_value
#     if type(base_value) == np.ndarray and len(base_value) == 1:
#         base_value = base_value[0]

#     if isinstance(base_value, list) or isinstance(shap_values, list):
#         raise TypeError("Looks like multi output. Try base_value[i] and shap_values[i], "
#                         "or use shap.multioutput_decision_plot().")

    # validate shap_values
    if not isinstance(shap_values, np.ndarray):
        raise TypeError("The shap_values arg is the wrong type. Try explainer.shap_values().")

    # calculate the various dimensions involved (observations, features, interactions, display, etc.
    if shap_values.ndim == 1:
        shap_values = shap_values.reshape(1, -1)
    observation_count = shap_values.shape[0]
    feature_count = shap_values.shape[1]
    # code taken from force_plot. convert features from other types.
    if str(type(features)) == "<class 'pandas.core.frame.DataFrame'>":
        if feature_names is None:
            feature_names = features.columns.to_list()
        features = features.values
    elif str(type(features)) == "<class 'pandas.core.series.Series'>":
        if feature_names is None:
            feature_names = features.index.to_list()
        features = features.values
    elif isinstance(features, list):
        if feature_names is None:
            feature_names = features
        features = None
    elif features is not None and features.ndim == 1 and feature_names is None:
        feature_names = features.tolist()
        features = None

    # the above code converts features to either None or np.ndarray. if features is something else at this point,
    # there's a problem.
    if not isinstance(features, (np.ndarray, type(None))):
        raise TypeError("The features arg uses an unsupported type.")
    if (features is not None) and (features.ndim == 1):
        features = features.reshape(1, -1)

    # validate/generate feature_names. at this point, feature_names does not include interactions.
    if feature_names is None:
        feature_names = [labels['FEATURE'] % str(i) for i in range(feature_count)]
    elif len(feature_names) != feature_count:
        raise ValueError("The feature_names arg must include all features represented in shap_values.")
    elif not isinstance(feature_names, list):
        raise TypeError("The feature_names arg requires a list or numpy array.")
    # transform interactions cube to a matrix and generate interaction names.
    if shap_values.ndim == 3:
        # flatten
        triu_count = feature_count * (feature_count - 1) // 2
        idx_diag = np.diag_indices_from(shap_values[0])
        idx_triu = np.triu_indices_from(shap_values[0], 1)
        a = np.ndarray((observation_count, feature_count + triu_count), shap_values.dtype)
        a[:, :feature_count] = shap_values[:, idx_diag[0], idx_diag[1]]
        a[:, feature_count:] = shap_values[:, idx_triu[0], idx_triu[1]] * 2
        shap_values = a
        # names
        a = [None] * shap_values.shape[1]
        a[:feature_count] = feature_names
        for i, row, col in zip(range(feature_count, shap_values.shape[1]), idx_triu[0], idx_triu[1]):
            a[i] = "{0} *\n{1}".format(feature_names[row], feature_names[col])
        feature_names = a
        feature_count = shap_values.shape[1]
        features = None  # Can't use feature values for interactions...

    # determine feature order
    if isinstance(feature_order, list):
        feature_idx = np.array(feature_order)
    elif isinstance(feature_order, np.ndarray):
        feature_idx = feature_order
    elif (feature_order is None) or (feature_order.lower() == "none"):
        feature_idx = np.arange(feature_count)
    elif feature_order is "importance":
        feature_idx = np.argsort(np.sum(np.abs(shap_values), axis=0))
    elif feature_order is "hclust":
        feature_idx = np.array(hclust_ordering(shap_values.transpose()))
    else:
        raise ValueError("The feature_order arg requires 'importance', 'hclust', 'none', or an integer list/array "
                         "of feature indices.")

    if (feature_idx.shape != (feature_count, )) or (not np.issubdtype(feature_idx.dtype, np.integer)):
        raise ValueError("A list or array has been specified for the feature_order arg. The length must match the "
                         "feature count and the data type must be integer.")

    # validate and convert feature_display_range to a slice. prevents out of range errors later.
    if feature_display_range is None:
        feature_display_range = slice(-1, -21, -1)  # show last 20 features in descending order.
    elif not isinstance(feature_display_range, (slice, range)):
        raise TypeError("The feature_display_range arg requires a slice or a range.")
    elif feature_display_range.step not in (-1, 1, None):
        raise ValueError("The feature_display_range arg supports a step of 1, -1, or None.")
    elif isinstance(feature_display_range, range):
        # Negative values in a range are not the same as negs in a slice. Consider range(2, -1, -1) == [2, 1, 0],
        # but slice(2, -1, -1) == [] when len(features) > 2. However, range(2, -1, -1) == slice(2, -inf, -1) after
        # clipping.
        a = np.iinfo(np.integer).min
        feature_display_range = slice(
            feature_display_range.start if feature_display_range.start >= 0 else a, 
            feature_display_range.stop if feature_display_range.stop >= 0 else a,
            feature_display_range.step
        )

    # apply new_base_value
    if new_base_value is not None:
        shap_values = __change_shap_base_value(base_value, new_base_value, shap_values)
        base_value = new_base_value

    # use feature_display_range to determine which features will be plotted. convert feature_display_range to
    # ascending indices and expand by one in the negative direction. why? we are plotting the change in prediction
    # for every feature. this requires that we include the value previous to the first displayed feature
    # (i.e. i_0 - 1 to i_n).
    a = feature_display_range.indices(feature_count)
    
    ascending = True
    if a[2] == -1:  # The step
        ascending = False
        a = (a[1] + 1, a[0] + 1, 1)
    feature_display_count = a[1] - a[0]
    shap_values = shap_values[:, feature_idx]
    if a[0] == 0:
        cumsum = np.ndarray((observation_count, feature_display_count + 1), shap_values.dtype)
        cumsum[:, 0] = base_values
        cumsum[:, 1:] = base_values.reshape(shap_values.shape[0],1) + np.nancumsum(shap_values[:, 0:a[1]], axis=1)
    else:
        cumsum = base_values.reshape(shap_values.shape[0],1) + np.nancumsum(shap_values, axis=1)[:, (a[0] - 1):a[1]]

    
    # Select and sort feature names and features according to the range selected above
    feature_names = np.array(feature_names)
    feature_names_display = feature_names[feature_idx[a[0]:a[1]]].tolist()
    feature_names = feature_names[feature_idx].tolist()
    features_display = None if features is None else features[:, feature_idx[a[0]:a[1]]]

    # throw large data errors
    if not ignore_warnings:
        if observation_count > 2000:
            raise RuntimeError("Plotting {} observations may be slow. Consider subsampling or set "
                               "ignore_warnings=True to ignore this message.".format(observation_count))
        if feature_display_count > 200:
            raise RuntimeError("Plotting {} features may create a very large plot. Set "
                               "ignore_warnings=True to ignore this "
                               "message.".format(feature_display_count))
        if feature_count * observation_count > 100000000:
            raise RuntimeError("Processing SHAP values for {} features over {} observations may be slow. Set "
                               "ignore_warnings=True to ignore this "
                               "message.".format(feature_count, observation_count))

    # convert values based on link and update x-axis extents
    create_xlim = xlim is None
    link = convert_to_link(link)
    
    base_value_saved = base_values[0]
    base_value = base_values[0]
    if isinstance(link, LogitLink):
        link_logit=True
        base_value = link.finv(base_value)
        cumsum = link.finv(cumsum)
        if create_xlim:
            # Expand [0, 1] limits a little for a visual margin
            xlim = (-0.02, 1.02)
    elif create_xlim:
        xmin = np.min((cumsum.min(), base_value))
        xmax = np.max((cumsum.max(), base_value))
        # create a symmetric axis around base_value
        a, b = (base_value - xmin), (xmax - base_value)
        if a > b:
            xlim = (base_value - a, base_value + a)
        else:
            xlim = (base_value - b, base_value + b)
        # Adjust xlim to include a little visual margin.
        a = (xlim[1] - xlim[0]) * 0.02
        xlim = (xlim[0] - a, xlim[1] + a)

    # Initialize style arguments
    if alpha is None:
        alpha = 1.0

    if plot_color is None:
        plot_color = red_blue
    decision_plot_matplotlib(base_values, cumsum,
        ascending,
        feature_display_count,
        features_display,
        feature_names_display,
        highlight,
        plot_color,
        axis_color,
        y_demarc_color,
        xlim,
        alpha,
        color_bar,
        auto_size_plot,
        title,
        show,
        legend_labels,
        legend_location,
        link_logit)

    if not return_objects:
        return None

    