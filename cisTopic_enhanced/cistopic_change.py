def run_cgs_models(
    cistopic_obj: "cisTopicObject",
    n_topics: List[int],
    n_cpu: Optional[int] = 1,
    n_iter: Optional[int] = 150,
    random_state: Optional[int] = 555,
    alpha: Optional[float] = 50,
    alpha_by_topic: Optional[bool] = True,
    eta: Optional[float] = 0.1,
    eta_by_topic: Optional[bool] = False,
    top_topics_coh: Optional[int] = 5,
    save_path: Optional[str] = None,
    **kwargs,
):
    """
    Run Latent Dirichlet Allocation using Gibbs Sampling as described in Griffiths and Steyvers, 2004.

    Parameters
    ----------
    cistopic_obj: cisTopicObject
        A :class:`cisTopicObject`. Note that cells/regions have to be filtered before running any LDA model.
    n_topics: list of int
        A list containing the number of topics to use in each model.
    n_cpu: int, optional
        Number of cpus to use for modelling. In this function parallelization is done per model, that is, one model will run entirely in a unique cpu. We recommend to set the number of cpus as the number of models that will be inferred, so all models start at the same time.
    n_iter: int, optional
        Number of iterations for which the Gibbs sampler will be run. Default: 150.
    random_state: int, optional
        Random seed to initialize the models. Default: 555.
    alpha: float, optional
        Scalar value indicating the symmetric Dirichlet hyperparameter for topic proportions. Default: 50.
    alpha_by_topic: bool, optional
        Boolean indicating whether the scalar given in alpha has to be divided by the number of topics. Default: True
    eta: float, optional
        Scalar value indicating the symmetric Dirichlet hyperparameter for topic multinomials. Default: 0.1.
    eta_by_topic: bool, optional
        Boolean indicating whether the scalar given in beta has to be divided by the number of topics. Default: False
    top_topics_coh: int, optional
        Number of topics to use to calculate the model coherence. For each model, the coherence will be calculated as the average of the top coherence values. Default: 5.
    save_path: str, optional
        Path to save models as independent files as they are completed. This is recommended for large data sets. Default: None.

    Return
    ------
    list of :class:`CistopicLDAModel`
        A list with cisTopic LDA models.

    References
    ----------
    Griffiths, T. L., & Steyvers, M. (2004). Finding scientific topics. Proceedings of the National academy of Sciences, 101(suppl 1), 5228-5235.
    """

    binary_matrix = sparse.csr_matrix(
        cistopic_obj.binary_matrix.transpose(), dtype=np.integer
    )
    region_names = cistopic_obj.region_names
    cell_names = cistopic_obj.cell_names
    #ray.init(num_cpus=n_cpu, **kwargs)
    model_list = ray.get(
        [
            run_cgs_model.remote(
                binary_matrix,
                n_topics=n_topic,
                cell_names=cell_names,
                region_names=region_names,
                n_iter=n_iter,
                random_state=random_state,
                alpha=alpha,
                alpha_by_topic=alpha_by_topic,
                eta=eta,
                eta_by_topic=eta_by_topic,
                top_topics_coh=top_topics_coh,
                save_path=save_path,
            )
            for n_topic in n_topics
        ]
    )
    #ray.shutdown()
    return model_list

def find_diff_features(
    cistopic_obj: "CistopicObject",
    imputed_features_obj: "CistopicImputedFeatures",
    variable: str,
    var_features: Optional[List[str]] = None,
    contrasts: Optional[List[List[str]]] = None,
    adjpval_thr: Optional[float] = 0.05,
    log2fc_thr: Optional[float] = np.log2(1.5),
    n_cpu: Optional[int] = 1,
    split_pattern: Optional[str] = "___",
    **kwargs,
):
    """
    Find differential imputed features.

    Parameters
    ---------
    cistopic_obj: `class::CistopicObject`
        A cisTopic object including the cells in imputed_features_obj.
    imputed_features_obj: :class:`CistopicImputedFeatures`
        A cisTopic imputation data object.
    variable: str
        Name of the group variable to do comparison. It must be included in `class::CistopicObject.cell_data`
    var_features: list, optional
        A list of features to use (e.g. variable features from `find_highly_variable_features()`)
    contrast: List, optional
        A list including contrasts to make in the form of lists with foreground and background, e.g.
        [[['Group_1'], ['Group_2, 'Group_3']], []['Group_2'], ['Group_1, 'Group_3']], []['Group_1'], ['Group_2, 'Group_3']]].
        Default: None.
    adjpval_thr: float, optional
        Adjusted p-values threshold. Default: 0.05
    log2fc_thr: float, optional
        Log2FC threshold. Default: np.log2(1.5)
    n_cpu: int, optional
        Number of cores to use. Default: 1
    **kwargs
        Parameters to pass to ray.init()

    Return
    ------
    List
        List of `class::pd.DataFrame` per contrast with the selected features and logFC and adjusted p-values.
    """
    # Create cisTopic logger
    level = logging.INFO
    log_format = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    handlers = [logging.StreamHandler(stream=sys.stdout)]
    logging.basicConfig(level=level, format=log_format, handlers=handlers)
    log = logging.getLogger("cisTopic")

    selected_cells = list(
        set(cistopic_obj.cell_data.index.tolist())
        & set(imputed_features_obj.cell_names)
    )
    group_var = cistopic_obj.cell_data.loc[selected_cells, variable].dropna()
    if contrasts is None:
        levels = sorted(list(set(group_var.tolist())))
        contrasts = [
            [[x], levels[: levels.index(x)] + levels[levels.index(x) + 1 :]]
            for x in levels
        ]
        contrasts_names = levels
    else:
        contrasts_names = [
            "_".join(contrasts[i][0]) + "_VS_" + "_".join(contrasts[i][1])
            for i in range(len(contrasts))
        ]
    # Get barcodes in each class per contrats
    barcode_groups = [
        [
            group_var[group_var.isin(contrasts[x][0])].index.tolist(),
            group_var[group_var.isin(contrasts[x][1])].index.tolist(),
        ]
        for x in range(len(contrasts))
    ]
    # Subset imputed accessibility matrix
    subset_imputed_features_obj = imputed_features_obj.subset(
        cells=None, features=var_features, copy=True, split_pattern=split_pattern
    )
    # Convert to csc
    if sparse.issparse(subset_imputed_features_obj.mtx):
        mtx = subset_imputed_features_obj.mtx.tocsc()
    # Compute p-val and log2FC
    if n_cpu > 1:
        #ray.init(num_cpus=n_cpu, **kwargs)
        markers_list = ray.get(
            [
                markers_ray.remote(
                    subset_imputed_features_obj,
                    barcode_groups[i],
                    contrasts_names[i],
                    adjpval_thr=adjpval_thr,
                    log2fc_thr=log2fc_thr,
                )
                for i in range(len(contrasts))
            ]
        )
        #ray.shutdown()
    else:
        markers_list = [
            markers_one(
                subset_imputed_features_obj,
                barcode_groups[i],
                contrasts_names[i],
                adjpval_thr=adjpval_thr,
                log2fc_thr=log2fc_thr,
            )
            for i in range(len(contrasts))
        ]
    markers_dict = {
        contrasts_names[i]: markers_list[i] for i in range(len(markers_list))
    }
    return markers_dict

