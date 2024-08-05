import astropy.units as un
import dask.array as da
import numpy as np
import xarray as xr
from pyralysis.base import Dataset
from pyralysis.estimators import BilinearInterpolation
from pyralysis.reconstruction import Image
from pyralysis.units import array_unit_conversion


def _new_image(cellsize, image_size) -> Image:
    X, Y = np.mgrid[0:image_size, 0:image_size]
    image = Image(
        data=xr.DataArray(
            data=da.zeros((image_size, image_size), chunks=(image_size, image_size)),
            dims=["x", "y"],
            coords=dict(X=(["x", "y"], Y), Y=(["x", "y"], X)),
        ),
        cellsize=cellsize,
        chunks=(image_size, image_size),
    )
    image_cellsize = image.cellsize.to(un.deg)
    image.data.attrs["CDELT1"] = image_cellsize[0].value
    image.data.attrs["CDELT2"] = image_cellsize[1].value
    return image


def _get_image_delta(image: Image) -> tuple:
    return image.cellsize.to(un.rad).value


def _get_image_indices(image: Image) -> tuple:
    index_x, index_y, *_ = da.indices(
        image.data.data.shape, dtype=np.int32, chunks=image.data.data.chunksize
    )
    ravel_index_x = index_x.ravel()
    ravel_index_y = index_y.ravel()
    return ravel_index_x, ravel_index_y


def _get_direction_phase(field, delta, image_shape, i):
    return (field.phase_direction_cosines[i].value / delta + image_shape // 2).astype(
        np.float32
    )


def _get_image_ms_coord(field_id, phase_center, delta, cell):
    phase_dir = phase_center[field_id] * delta
    coord = cell - np.float32(phase_dir)
    return coord


def process_model_visibilities(alma: Dataset) -> Dataset:
    image = _new_image(alma.theo_resolution / 7, 64)
    model_visibility = BilinearInterpolation(
        input_data=alma,
        image=image,
        cellsize=alma.theo_resolution / 7,
        hermitian_symmetry=False,
        padding_factor=1.0,
    )
    model_visibility.transform()
    alma = model_visibility.input_data
    return alma, image


def _get_weights_ms(data, flag, n_channels, correlation):
    weight_broadcasted = da.repeat(data[:, np.newaxis, :], n_channels, axis=1)
    weight_broadcasted *= ~flag
    weight_filtered = weight_broadcasted[:, :, correlation]
    return weight_filtered


def _get_uvw_lambda_ms(data, equivalencies, n_channels):
    uvw_broadcast = da.repeat(data[:, np.newaxis, :], n_channels, axis=1)
    uvw_lambdas = array_unit_conversion(
        array=uvw_broadcast, unit=un.lambdas, equivalencies=equivalencies
    )
    return uvw_lambdas


def process_data_idft2(alma_model_visibilities, alma_image):
    delta_x, delta_y = _get_image_delta(alma_image)
    index_x, index_y = _get_image_indices(alma_image)
    x_cell = (index_x * delta_x).astype(np.float32)
    y_cell = (index_y * delta_y).astype(np.float32)
    l_direction_phase_pixels = _get_direction_phase(
        alma_model_visibilities.field, delta_x, alma_image.data.shape[-1], 0
    )
    m_direction_phase_pixels = _get_direction_phase(
        alma_model_visibilities.field, delta_y, alma_image.data.shape[-2], 1
    )

    CORR = ["XX", "YY", "RR", "LL"]
    idft2_input = {}

    for index, ms in enumerate(alma_model_visibilities.ms_list):
        field_id = ms.field_id
        x = _get_image_ms_coord(field_id, l_direction_phase_pixels, delta_x, x_cell)
        y = _get_image_ms_coord(field_id, m_direction_phase_pixels, delta_y, y_cell)

        weights_data = ms.visibilities.imaging_weight.data
        flag = ms.visibilities.flag.data
        spw_id = ms.spw_id
        pol_id = ms.polarization_id
        n_channels = alma_model_visibilities.spws.nchans[spw_id]
        correlation_names = alma_model_visibilities.polarization.corrs_string[pol_id]
        correlation = [x in CORR for x in correlation_names]
        weights = _get_weights_ms(weights_data, flag, n_channels, correlation)

        model_visibilities = ms.visibilities.model.data
        observed_visibilities = ms.visibilities.data.data
        residual_visibilities = observed_visibilities - model_visibilities
        visibilities = residual_visibilities[:, :, correlation]

        equivalencies = alma_model_visibilities.spws.equivalencies[spw_id]
        uvw_data = ms.visibilities.uvw.data.astype(np.float32) * un.m
        uvw = _get_uvw_lambda_ms(uvw_data, equivalencies, n_channels)

        idft2_input[index] = {
            "x": x,
            "y": y,
            "uvw": uvw,
            "visibilities": visibilities,
            "weights": weights,
        }

    return idft2_input
