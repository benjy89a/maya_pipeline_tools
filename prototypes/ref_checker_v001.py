import maya.cmds as cmds
import pathlib
from core import path_parser


def check_all_references():
    all_refs = cmds.file(q=True, reference=True)
    if not all_refs:
        raise RuntimeError("There is no reference file.")

    latest_cache = {}

    print("\n" + "=" * 60)
    print(f"{'NAMESPACE':<20} | {'CURRENT':<10} | {'LATEST':<10} | STATUS")
    print("-" * 60)

    for ref_path in set(all_refs):
        ref_info = path_parser.PathParser.create(ref_path)
        folder_path = ref_info.dirpath

        maya_files = list(folder_path.glob("*.ma"))

        base_name = ref_info.base_name
        latest_info = ref_info

        for f in maya_files:
            if f.stem.startswith(base_name):
                temp_info = path_parser.PathParser(str(f))
                if temp_info.version is not None:
                    if latest_info.version is None or temp_info.version > latest_info.version:
                        latest_info = temp_info

        latest_cache[ref_path] = latest_info

    for ref_path in all_refs:
        try:
            ns = cmds.referenceQuery(ref_path, namespace=True, shortName=True)
        except RuntimeError:
            ns = "Unknown"

        current_info = path_parser.PathParser.create(ref_path)
        latest_info = latest_cache[ref_path]

        current_ver = current_info.get_version_str()
        latest_ver = latest_info.get_version_str()

        status = "OK"
        if current_info.version and latest_info.version:
            if current_info.version < latest_info.version:
                status = "UPDATE NEEDED"

        print(f"{ns:<20} | {current_ver:<10} | {latest_ver:<10} | {status}")

    print("=" * 60 + "\n")
