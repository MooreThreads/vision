"""MUSA build utils"""
from pathlib import Path
import platform

import torch, torch_musa
from torch_musa.utils.musa_extension import MUSAExtension, BuildExtension


def _get_cpu_arch():
    if any(x in platform.machine() for x in ["arm", "aarch64"]):
        return "arm"
    if any(x in platform.machine() for x in ["x86", "x64"]):
        return "x86"
    raise ValueError(f"Unidentified CPU arch: {platform.machine()}")


def make_MUSA_build_ext():
    return BuildExtension


def make_MUSA_C_extension():
    print("Building MUSA _C extension")

    ROOT_DIR = Path(__file__).absolute().parent
    CSRS_DIR = ROOT_DIR / "torchvision" / "csrc" / "ops" / "musa"

    sources = list(CSRS_DIR.glob("*.mu"))

    torch_musa_dir = Path(torch_musa.__file__).parent
    if Path.exists(torch_musa_dir / "torch_musa"):
        torch_musa_dir = torch_musa_dir / "torch_musa"
    print(torch_musa_dir)

    include_dirs = [CSRS_DIR] + [
        torch_musa_dir.parent,
        torch_musa_dir / "share" / "torch_musa_codegen",
        torch_musa_dir / "share" / "generated_cuda_compatible" / "include",
        torch_musa_dir / "share" / "generated_cuda_compatible" / "include" / "torch" / "csrc" / "api" / "include",
    ]

    cxx_flags = [
        "-O3",
        "-fvisibility=hidden",
        "-std=c++17",
        "-Wno-reorder",
        "force_mcc",
    ]
    mcc_flags = [
        "-O3",
    ]

    if _get_cpu_arch() != "arm":
        cxx_flags.append("-march=native")
        mcc_flags.append("-march=native")

    library_dirs = [torch_musa_dir / "lib"]
    libraries = ["musa_kernels", "musa_python"]

    return MUSAExtension(
        name="torchvision._MUSAC",
        sources=sorted(str(s) for s in sources),
        include_dirs=[str(include_dir) for include_dir in include_dirs],
        extra_compile_args={
            "cxx": cxx_flags,
            "mcc": mcc_flags,
        },
        library_dirs=[str(lib_dir) for lib_dir in library_dirs],
        libraries=[str(lib) for lib in libraries],
    )
