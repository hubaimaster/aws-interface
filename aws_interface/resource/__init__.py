from resource.aws import AWSResource, AWSResourceAllocator


def get_resource(vendor, credential, app_id, vendor_session=None):
    if vendor == 'aws':
        return AWSResource(credential, app_id, vendor_session)
    raise BaseException('No vendor name which is {}'.format(vendor))


def get_resource_allocator(vendor, credential, app_id, recipes):
    if vendor == 'aws':
        return AWSResourceAllocator(credential, app_id, recipes)
    raise BaseException('No vendor name which is {}'.format(vendor))
