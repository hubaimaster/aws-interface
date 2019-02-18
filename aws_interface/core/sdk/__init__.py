import importlib
import json
import os
import shutil
import tempfile
from core.recipecontroller import RecipeController
from core.servicecontroller import ServiceController


def generate(controller_pairs):
    """
    Generate the sdk for the given recipe types.

    :param controller_pairs
    List of tuples of (RecipeController, ServiceController) pairs

    :return: Binary of zipfile
    """
    manifest = _generate_manifest(controller_pairs)

    platform_packages = [
        'core.sdk.java',
        'core.sdk.javascript',
        'core.sdk.python3',
        'core.sdk.swift'
    ]

    tmp_dir = tempfile.mkdtemp()

    for platform_package in platform_packages:
        # Copy source files
        platform = platform_package.split('.')[-1]
        platform_dir = os.path.join(tmp_dir, platform)
        module = importlib.import_module(platform_package)
        module_path = os.path.dirname(module.__file__)
        shutil.copytree(module_path, platform_dir)
        try:
            os.remove(os.path.join(platform_dir, '__init__.py'))
            shutil.rmtree(os.path.join(platform_dir, '__pycache__'))
        except BaseException as ex:
            print(ex)

        # Write manifest.json
        with open(os.path.join(platform_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f)

    # Archive all files and extract binary
    output_filename = tempfile.mktemp()
    shutil.make_archive(output_filename, 'zip', tmp_dir)
    zip_file = '{}.zip'.format(output_filename)
    with open(zip_file, 'rb') as f:
        zip_file_bin = f.read()

    # Remove temp files
    os.remove(zip_file)
    shutil.rmtree(tmp_dir)

    return zip_file_bin


def _generate_manifest(controller_pairs):
    manifest = dict()

    # Initialize list of recipe types
    manifest['recipe_types'] = list()

    # Populate manifest
    rc: RecipeController
    sc: ServiceController
    for rc, sc in controller_pairs:
        recipe_type = rc.get_recipe_type()

        recipe_manifest = {
            'rest_api_url': sc.get_rest_api_url(rc),
            'cloud_apis': list(rc.get_cloud_apis),
        }

        manifest['recipe_types'].append(recipe_type)
        manifest[recipe_type] = recipe_manifest

    return manifest



