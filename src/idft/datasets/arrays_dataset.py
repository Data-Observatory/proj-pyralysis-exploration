from pathlib import PurePosixPath
from typing import Any, Dict

import cupy as cp
import dask.array as da
import zarr
from kedro.io import AbstractDataset
from kedro.io.core import get_protocol_and_path


class GroupedArraysDataset(AbstractDataset):
    def __init__(self, filepath: str, overwrite: bool = True):
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)
        self._overwrite = overwrite

    def _load(self) -> Dict[str, da.Array]:
        group = zarr.open_group(store=self._filepath.as_posix(), mode="r")
        group_url = group.store.dir_path()
        idft2_input = {}
        for ms_group_name in group.keys():
            index = int(ms_group_name.split("_")[1])
            idft2_input[index] = {
                "x": da.from_zarr(url=group_url, component=f"{ms_group_name}/x"),
                "y": da.from_zarr(url=group_url, component=f"{ms_group_name}/y"),
                "uvw": da.from_zarr(url=group_url, component=f"{ms_group_name}/uvw"),
                "visibilities": da.from_zarr(
                    url=group_url, component=f"{ms_group_name}/visibilities"
                ),
                "weights": da.from_zarr(
                    url=group_url, component=f"{ms_group_name}/weights"
                ),
            }
        return idft2_input

    def _save(self, data: Dict) -> None:
        store = zarr.DirectoryStore(self._filepath.as_posix())
        group = zarr.group(store=store, overwrite=self._overwrite)
        group_path = group.store.dir_path()
        for index, arrays in data.items():
            ms_group = group.create_group(f"ms_{index}")
            ms_path = f"{group_path}{ms_group.name}"
            da.to_zarr(arrays["x"], url=ms_path, component="x")
            da.to_zarr(arrays["y"], url=ms_path, component="y")
            da.to_zarr(arrays["uvw"], url=ms_path, component="uvw")
            da.to_zarr(arrays["visibilities"], url=ms_path, component="visibilities")
            da.to_zarr(arrays["weights"], url=ms_path, component="weights")

    def _describe(self) -> Dict[str, Any]:
        return dict(filepath=self._filepath, overwrite=self._overwrite)


class GroupedCupyArraysDataset(GroupedArraysDataset):
    def _load(self) -> Dict[str, Any]:
        meta_array = cp.empty(())
        group = zarr.open_group(
            self._filepath.as_posix(), mode="r", meta_array=meta_array
        )
        group_url = group.store.dir_path()
        idft2_input = {}
        for ms_group_name in group.keys():
            index = int(ms_group_name.split("_")[1])
            idft2_input[index] = {
                "x": da.from_zarr(
                    url=group_url, component=f"{ms_group_name}/x", meta_array=meta_array
                ),
                "y": da.from_zarr(
                    url=group_url, component=f"{ms_group_name}/y", meta_array=meta_array
                ),
                "uvw": da.from_zarr(
                    url=group_url,
                    component=f"{ms_group_name}/uvw",
                    meta_array=meta_array,
                ),
                "visibilities": da.from_zarr(
                    url=group_url,
                    component=f"{ms_group_name}/visibilities",
                    meta_array=meta_array,
                ),
                "weights": da.from_zarr(
                    url=group_url,
                    component=f"{ms_group_name}/weights",
                    meta_array=meta_array,
                ),
            }
        return idft2_input
