from django.http import JsonResponse
import logging

from ..constants import ALLOWED_RESOURCE_TYPES
from ..decorators import require_valid_token
from ..errors import build_error_response, method_not_allowed

from apps.fhir.bluebutton.utils import (request_call,
                                        get_host_url,
                                        post_process_request,
                                        get_crosswalk,
                                        get_resourcerouter,
                                        build_rewrite_list,
                                        get_response_text)

logger = logging.getLogger('hhs_server.%s' % __name__)


@require_valid_token()
def read(request, resource_type, resource_id, *args, **kwargs):
    """
    Read from Remote FHIR Server
    # Example client use in curl:
    # curl -X GET http://127.0.0.1:8000/fhir/Patient/1234
    """

    logger.debug("resource_type: %s" % resource_type)
    logger.debug("Interaction: read")
    logger.debug("Request.path: %s" % request.path)

    if request.method != 'GET':
        return method_not_allowed(['GET'])

    if resource_type not in ALLOWED_RESOURCE_TYPES:
        logger.info('User requested read access to the %s resource type' % resource_type)
        return build_error_response(404, 'The requested resource type, %s, is not supported'
                                         % resource_type)

    crosswalk = get_crosswalk(request.resource_owner)

    # If the user isn't matched to a backend ID, they have no permissions
    if crosswalk is None:
        logger.info('Crosswalk for %s does not exist' % request.user)
        return build_error_response(403, 'No access information was found for the authenticated user')

    resource_router = get_resourcerouter(crosswalk)

    if resource_type == 'Patient':
        # Error out in advance for non-matching Patient records.
        # Other records must hit backend to check permissions.
        if resource_id != crosswalk.fhir_id:
            return build_error_response(403, 'You do not have permission to access data on the requested patient')

        resource_id = crosswalk.fhir_id

    target_url = resource_router.fhir_url + resource_type + "/" + resource_id + "/"

    logger.debug('FHIR URL with key:%s' % target_url)

    get_parameters = {
        "_format": "json"
    }

    logger.debug('Here is the URL to send, %s now add '
                 'GET parameters %s' % (target_url, get_parameters))

    # Now make the call to the backend API

    response = request_call(request, target_url, crosswalk, timeout=None, get_parameters=get_parameters)

    if response.status_code == 404:
        return build_error_response(404, 'The requested resource does not exist')

    # TODO: This should be more specific
    if response.status_code >= 300:
        return build_error_response(502, 'An error occurred contacting the upstream server')

    # Now check that the user has permission to access the data
    # Patient resources were taken care of above
    # Return 404 on error to avoid notifying unauthorized user the object exists
    try:
        if resource_type == 'Coverage':
            reference = response._json()['beneficiary']['reference']
            reference_id = reference.split('|')[1]
            if reference_id != crosswalk.fhir_id:
                return standard_404()
        elif resource_type == 'ExplanationOfBenefit':
            reference = response._json()['patient']['reference']
            reference_id = reference.split('|')[1]
            if reference_id != crosswalk.fhir_id:
                return standard_404()
    except Exception:
        logger.warning('An error occurred fetching beneficiary id')
        return standard_404()

    host_path = get_host_url(request, resource_type)[:-1]

    # Add default FHIR Server URL to re-write
    rewrite_url_list = build_rewrite_list(crosswalk)
    text_in = get_response_text(fhir_response=response)
    text_out = post_process_request(request, host_path, text_in, rewrite_url_list)

    return JsonResponse(text_out)


def standard_404():
    return build_error_response(404, 'The requested resource does not exist')
