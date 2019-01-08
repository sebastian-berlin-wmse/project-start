import logging
from time import time
from time import sleep

import requests

"""
Attributes
----------
API_TOKEN : str
    Token to use when sending requests to the Conduit API.
API_URL : str
    URL to the Phabricator API to send requests to.
PARENT_PROJECT_ID : int
    Id of the project that will be parent project for all added
    projects. This can be found in the URL for the profile page of a
    project. E.g. in
    https://phabricator.wikimedia.org/project/profile/2480/ the
    project id is 2048.
REQUEST_DELAY : float
    Minimum time between requests, in seconds.
"""

API_TOKEN = "api-..."
API_URL = "https://.../api"
PARENT_PROJECT_ID = 0
REQUEST_DELAY = 10.0


class Phab:
    """Handles Phabricator interaction.

    Uses the Conduit API for requests.

    Attributes
    ----------
    _dry_run : bool
        If True, no data is written to Phabricator.
    _last_request_time : float
        Time when last request was made, in seconds.
    """

    def __init__(self, dry_run):
        self._dry_run = dry_run
        self._last_request_time = 0.0

    def add_project(self, name, description):
        """Add project.

        Parameters
        ----------
        name : str
            Name of the project. This is modified to follow the
            conventions specified at:
            https://www.mediawiki.org/wiki/Phabricator/Creating_and_renaming_projects#Good_practices_for_name_and_description
        description : str
            Description of the project in English. This is added as
            description in the project.

        Returns
        -------
        tuple
            Project id and name of the project that was created.

        """
        phab_name = self._to_phab_project_name(name)
        if self._dry_run:
            return 1, phab_name
        parent_phid = self._get_project_phid(PARENT_PROJECT_ID)
        parameters = {
            "transactions": {
                "0": {
                    "type": "name",
                    "value": phab_name
                },
                "1": {
                    "type": "description",
                    "value": description
                },
                "2": {
                    "type": "parent",
                    "value": parent_phid
                }
            }
        }
        response = self._make_request("project.edit", parameters)
        project_id = response["result"]["object"]["id"]
        return project_id, phab_name

    def _get_project_phid(self, id_):
        """Get the PHID of a project.

        The format of the PHID is "PHID-PROJ-..." for projects. Note
        that this is not the same as the project id, which is just a
        number. Uses the endpoint "project.search".

        Parameters
        ----------
        id_ : int
            Id of the project to get PHID for.

        Returns
        -------
        str
            PHID for the given project.

        """
        parameters = {"constraints": {"ids": [id_]}}
        response = self._make_request("project.search", parameters)
        return response["result"]["data"][0]["phid"]

    def _make_request(self, endpoint, parameters_dict):
        """Make a request to the Conduit API.

        Parameters
        ----------
        endpoint_ : str
            Name of the endpoint to send the request to.
        parameters_dict : dict
            The parameters to send with the request.

        Returns
        -------
        dict
            Response from the API, parsed from Json.

        Raises
        ------
        PhabApiError
            If the Conduit API response contains an error.
        """
        wait_time = self._last_request_time - time() + REQUEST_DELAY
        if wait_time > 0:
            sleep(wait_time)
        parameters = self._to_phab_parameters(parameters_dict)
        parameters["api.token"] = API_TOKEN
        logging.debug(
            "POST to Phabricator API on {}: {}".format(API_URL, parameters)
        )
        self._last_request_time = time()
        response = requests.post(
            "{}/{}".format(API_URL, endpoint),
            parameters
        ).json()
        if response["error_info"]:
            raise PhabApiError("Error from Phabricator API: {}".format(
                response["error_info"]
            ))
        logging.debug("Response: {}".format(response))
        return response

    def _to_phab_parameters(
            self,
            dict_parameters,
            phab_parameters=None,
            prefix="",
            top=True
    ):
        """Convert a dict of parameters into Conduit request format.

        Conduit accepts structured parameters of the format:
            transactions[0][type]=parent
            transactions[0][value]=PHID-PROJ-ft7vbzykjs52i5vguajb
            transactions[1][type]=name
            transactions[1][value]=WMSE-Project
        These are mapped from a dict like:
            {
                "transactions": {
                    "0": {
                        "type": "parent",
                        "value": "PHID-PROJ-ft7vbzykjs52i5vguajb"
                    },
                    "1": {
                        "type": "name",
                        "value": "WMSE-Project"
                    }
                }
            }

        Parameters
        ----------
        dict_parameters : dict
            Input parameters.
        phab_parameters : dict
            Output parameters in the Conduit format. Parameters are
            added as they are discovered.
        prefix : str
            Prefix of a parameter name,
            e.g. "transactions[0][type]". This get extended when the
            function traverses along a parameter path.
        top : bool
            Whether the call is for a top level parameter. If True,
            square brackets aren't added when adding parameter name to
            prefix.

        Returns
        -------
        dict
            Parameters with names in the Conduit format.

        """
        if phab_parameters is None:
            phab_parameters = {}
        for key, value in dict_parameters.items():
            if type(value) is dict:
                if top:
                    new_prefix = "{}{}".format(prefix, key)
                else:
                    new_prefix = "{}[{}]".format(prefix, key)
                new_parameters = \
                    self._to_phab_parameters(
                        value,
                        phab_parameters,
                        new_prefix,
                        False
                    )
                phab_parameters.update(new_parameters)
            elif type(value) is list:
                for index, item in enumerate(value):
                    parameter_key = \
                        "{}[{}][{}]".format(prefix, key, index)
                    phab_parameters[parameter_key] = item
            else:
                parameter_key = "{}[{}]".format(prefix, key)
                phab_parameters[parameter_key] = value
        return phab_parameters

    def _to_phab_project_name(self, name):
        """Convert a project name to follow Wikimedia conventions.

        Replaces spaces with dashes.

        Parameters
        ----------
        name : str
            Project name.

        Returns
        -------
        str
            Project name with spaces replaced by dashes.

        """
        return name.replace(" ", "-")


class PhabApiError(Exception):
    """Raised when Conduit API returns an error."""
    pass
