# idft

## Overview

This is a Kedro project with Kedro-Viz and PySpark setup, which was generated using `kedro 0.19.6`.

## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file
* Make sure your results can be reproduced by following a [data engineering convention](https://docs.kedro.org/en/stable/faq/faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

The dependencias are declared in `requirements.txt` for `pip` installation.

To install them, run:

```
pip install -r requirements.txt
```

## How to add pipelines to the project

To create a new pipeline inside the project, run the following command:

```
kedro pipeline create <pipeline_name>
```

## How to run your Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

You can run the pipeline from a specific node with:

```
kedro run --from-nodes=process_data_idft2_node
```

## How to test your Kedro project

Have a look at the file `tests/test_run.py` for instructions on how to write your tests. Run the tests as follows:

```
pytest
```

To configure the coverage threshold, look at the `.coveragerc` file.

## How to contribute to this project

After installing the dependencies, run the pipeline modified, and check that everything is working.
This project has linting with ruff, and has pre-commit configured to check for code issues.

To install pre-commit run:

```
pip install pre-commit
```

To install the git hook scripts run:

```
pre-commit install
```

## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `catalog`, `context`, `pipelines` and `session`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `pip install -r requirements.txt` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can use tools like [`nbstripout`](https://github.com/kynan/nbstripout). For example, you can add a hook in `.git/config` with `nbstripout --install`. This will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Kedro project

[Further information about building project documentation and packaging your project](https://docs.kedro.org/en/stable/tutorial/package_a_project.html)

## Resources

- Take a look at the [Kedro documentation](https://docs.kedro.org) to get started.
- Check the [code formatting and linting](https://docs.kedro.org/en/stable/development/linting.html) page to run the tools.
- This project uses custom datasets. Check the [Tutorial to create a custom dataset](https://docs.kedro.org/en/stable/data/how_to_create_a_custom_dataset.html).
- [Further information about project dependencies](https://docs.kedro.org/en/stable/kedro_project_setup/dependencies.html#project-specific-dependencies)