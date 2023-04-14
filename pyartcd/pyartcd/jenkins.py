import base64
import logging
import os
import aiohttp
from jenkinsapi.jenkins import Jenkins

import constants

logger = logging.getLogger(__name__)


def _get_credentials():
    """
    Get username and password from environment variables.
    :return: tuple containing username and password
    """
    service_account = os.environ['JENKINS_SERVICE_ACCOUNT']
    token = os.environ['JENKINS_SERVICE_ACCOUNT_TOKEN']
    if not username or not password:
        raise RuntimeError('Jenkins account and token must be set in environment variables')
    return service_account, token


class JenkinsApi:
    def __init__(self):
        service_account, token = _get_credentials()
        self.J = Jenkins(constants.BUILDVM_URL, username=service_account, password=token)

    def trigger_job(self, job_path: str, params: dict = {}):
        job = self.J.get_job(job_path)
        b = job.invoke(build_params=params).block_until_building()
        b.block_until_complete()


async def trigger_jenkins_job(job_path: str, params: dict = {}):
    """
    Trigger a job using remote API calls.
    :param job_path: relative path to the job, starting from <buildvm hostname>:<jenkins port>
    :param params: optional dict containing job parameters
    """

    service_account, token = _get_credentials()

    build_url = os.environ.get('BUILD_URL', '')
    if build_url:
        params['TRIGGERED_FROM'] = build_url

    # Build authorization header
    auth = base64.b64encode(f'{service_account}:{token}'.encode()).decode()
    auth_header = f'Basic {auth}'
    headers = {'Authorization': auth_header}

    # Build url
    # If the job to be triggered is parametrized, use 'buildWithParameters' and send HTTP data
    # Otherwise, just call the 'build' endpoint with empty data
    url = f'{constants.BUILDVM_URL}/{job_path}'
    if params:
        url += '/buildWithParameters'
    else:
        url += '/build'

    # Call API endpoint
    logger.info('Triggering remote job /%s', job_path)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, data=params) as response:
            response.raise_for_status()
            await response.text()


async def trigger_ocp4(build_version: str):
    await trigger_jenkins_job(
        job_path='job/triggered-builds/job/ocp4',
        params={'BUILD_VERSION': build_version}
    )


async def trigger_rhcos(build_version: str, new_build: bool):
    await trigger_jenkins_job(
        job_path='job/triggered-builds/job/rhcos',
        params={'BUILD_VERSION': build_version, 'NEW_BUILD': new_build}
    )


async def trigger_build_sync(build_version: str):
    await trigger_jenkins_job(
        job_path='job/triggered-builds/job/build-sync',
        params={'BUILD_VERSION': build_version}
    )


async def trigger_build_microshift(build_version: str, assembly: str, dry_run: bool):
    await trigger_jenkins_job(
        job_path='job/triggered-builds/job/build-microshift',
        params={
            'BUILD_VERSION': build_version,
            'ASSEMBLY': assembly,
            'DRY_RUN': dry_run
        }
    )
