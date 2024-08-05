from pathlib import PurePosixPath
from typing import Any, Dict

import astropy.units as un
from astropy.io.fits import Header
from kedro.io import AbstractDataset
from kedro.io.core import get_protocol_and_path
from pyralysis.base.dataset import Dataset
from pyralysis.io import FITS, DaskMS
from pyralysis.io.zarr import ZarrDataset
from pyralysis.reconstruction import Image


class PyralysisDataset(AbstractDataset):
    def __init__(self, filepath: str):
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)

    def _load(self) -> Dataset:
        dataset_loader = DaskMS(input_name=self._filepath.as_posix())
        dataset = dataset_loader.read(filter_flag_column=False, calculate_psf=False)
        return dataset

    def _save(self, data: Dataset) -> None:
        save_path = self._filepath.as_posix()
        writer = ZarrDataset()
        writer.write(dataset=data, filename=save_path)

    def _describe(self) -> Dict[str, Any]:
        return dict(filepath=self._filepath)


class PyralysisZarrDataset(PyralysisDataset):
    def _load(self) -> Dataset:
        reader = ZarrDataset()
        dataset = reader.read(filename=self._filepath.as_posix())
        return dataset


class PyralysisImage(AbstractDataset):
    def __init__(self, filepath: str):
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)

    def _load(self) -> Image:
        image_loader = FITS(input_name=self._filepath.as_posix())
        image = image_loader.read()
        return image

    def _save(self, image: Image) -> None:
        writer = FITS(output_name=self._filepath.as_posix())
        cellsize_deg = image.cellsize.to(un.deg)
        header = Header(
            {"CDELT1": cellsize_deg[0].value, "CDELT2": cellsize_deg[1].value}
        )
        writer.write(image, header=header)

    def _describe(self) -> Dict[str, Any]:
        return dict(filepath=self._filepath)
