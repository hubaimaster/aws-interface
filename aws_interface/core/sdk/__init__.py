import importlib
import json
import os
import shutil
import tempfile
from core.recipecontroller import RecipeController
from core.servicecontroller import ServiceController


PLATFORMS = (
    'java',
    'javascript',
    'python3',
    'swift'
)


def generate(controller_pairs, platform):
    """
    Generate the sdk for the given recipe types.

    :param controller_pairs
    List of (RecipeController, ServiceController) pairs

    :param platform

    :return: Binary of zipfile
    """
    if platform not in PLATFORMS:
        raise ValueError('platform should be one of {}'.format(PLATFORMS))

    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(template_dir, 'templates')
    template_dir = os.path.join(template_dir, platform)
    print(template_dir)
    working_dir = tempfile.mkdtemp()
    sdk_dir = os.path.join(working_dir, 'sdk')

    shutil.copytree(template_dir, sdk_dir)
    manifest = _generate_manifest(controller_pairs)
    with open(os.path.join(sdk_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f)

    # Archive all files and extract binary
    output_filename = tempfile.mktemp()
    shutil.make_archive(output_filename, 'zip', sdk_dir)
    zip_file = '{}.zip'.format(output_filename)
    with open(zip_file, 'rb') as f:
        zip_file_bin = f.read()

    # Remove temp files
    os.remove(zip_file)
    shutil.rmtree(working_dir)

    return zip_file_bin


def _generate_manifest(controller_pairs):
    manifest = dict()

    # Initialize list of recipe types
    manifest['recipe_keys'] = list()

    # Populate manifest
    rc: RecipeController
    sc: ServiceController
    for rc, sc in controller_pairs:
        recipe_type = rc.RECIPE

        recipe_manifest = {
            'rest_api_url': sc.get_rest_api_url(rc),
            'cloud_apis': list(rc.get_cloud_apis()),
        }

        manifest['recipe_keys'].append(recipe_type)
        manifest[recipe_type] = recipe_manifest

    return manifest



