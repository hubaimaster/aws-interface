
import json
import os
import shutil
import tempfile


PLATFORMS = (
    'java',
    'javascript',
    'python3',
    'swift'
)


def generate(resource, platform):
    """
    Generate the sdk for the given recipe types.

    :param resource
    Instance of Resource class

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
    manifest = _generate_manifest(resource)
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


def _generate_manifest(resource):
    manifest = dict()

    rest_api_url = resource.get_rest_api_url()
    recipes = resource.get_recipes()

    # Initialize list of recipe types
    manifest['recipe_keys'] = list()

    # Populate manifest
    recipe: str
    for recipe in recipes:
        recipe = json.loads(recipe)
        recipe_type = recipe.get('recipe_type')

        recipe_manifest = {
            'rest_api_url': rest_api_url,
            'cloud_apis': list(recipe.get('cloud_apis', {})),
        }
        manifest['recipe_keys'].append(recipe_type)
        manifest[recipe_type] = recipe_manifest
    return manifest
