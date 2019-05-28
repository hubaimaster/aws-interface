"""This module is Getter of Resource and ResourceAllocator
The functions of this module should return Resource and ResourceAllocator's detail class as vendor

"""
import resource.aws


def get_resource(vendor, credential, app_id, vendor_session=None):
    """
    :param vendor: aws, azure, gcp, ...
    :param credential: Json authentication credential match to vendor
    :param app_id: App id for identification of aws-i application
    :param vendor_session:Like boto3, Needed when method called by vendor's server-less service
    :return: Resource's implementation instance case by vendor
    """
    if vendor == 'aws':
        return resource.aws.AWSResource(credential, app_id, vendor_session)
    raise BaseException('No vendor name which is {}'.format(vendor))


def get_resource_allocator(vendor, credential, app_id):
    """
    :param vendor: aws, azure, gcp, ...
    :param credential: Json authentication credential match to vendor
    :param app_id: App id for identification of aws-i application
    :return: ResourceAllocator's implementation instance case by vendor
    """
    if vendor == 'aws':
        return resource.aws.AWSResourceAllocator(credential, app_id)
    raise BaseException('No vendor name which is {}'.format(vendor))
