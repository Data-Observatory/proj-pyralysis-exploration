"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import process_data_idft2, process_model_visibilities


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=process_model_visibilities,
                inputs="alma",
                outputs=["alma_model_visibilities", "alma_image"],
                name="process_model_visibilities_node",
            ),
            node(
                func=process_data_idft2,
                inputs=["alma_model_visibilities", "alma_image"],
                outputs="idft2_input",
                name="process_data_idft2_node",
            ),
        ]
    )
