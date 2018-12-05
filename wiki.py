from pywikibot import Site
from pywikibot import Page

from template import Template

"""
Attributes
----------
PROJECT_NAMESPACE : str
    The namespace where the project pages will be created.

"""

PROJECT_NAMESPACE = "Projekt"


class Wiki:
    """Handles wiki interaction.

    Uses `pywikibot` to write to the wiki.

    Attributes
    ----------
    _site : Site
        `Site` object used by Pywikibot
    """

    def __init__(self):
        self._site = Site()

    def add_project_page(self, name, description, partners):
        """Add the main project page.

        Parameters
        ----------
        name : str
            The project name. This will be used as title for the page.
        description : str
            Passed to template as parameter "beskrivning".
        partners : str
            Passed to template as parameter "samarbetspartners".

        """
        template = Template("Projekt-sida", True)
        template.add_parameter("beskrivning", description)
        template.add_parameter("samarbetspartners", partners)
        page = Page(self._site, name, PROJECT_NAMESPACE)
        content = "{}".format(template)
        page.text = content
        page.save("[TEST] Skapa projektsida.")

    def add_volunteer_subpage(self, project, email_prefix):
        """Add a volunteer subpage under the project page.

        The title of this page is "Frivillig". It is created by
        substituting the template "Frivillig-sida".

        Parameters
        ----------
        project : str
            The project name.
        email_prefix : str
            Passed to template as parameter "e-post_prefix".

        """
        title = "Frivillig"
        summary = "[TEST] Skapa undersida för frivilliga."
        parameters = {"e-post_prefix": email_prefix}
        self._add_subpage(
            project,
            title,
            summary,
            "Frivillig-sida",
            parameters
        )

    def _add_subpage(
            self,
            project,
            title,
            summary,
            template_name,
            template_parameters={}
    ):
        """Add a  subpage under the project page.

        Parameters
        ----------
        project : str
            The project name.
        title : str
            The title of the subpage. Only the prefix, i.e. the
            substring after the last slash. This will be prepended by
            the project name to create the complete subpage title.
        summary : str
            The summary that will be used for the edit.
        template_name : str
            The name of the template to substitute to create the subpage.
        template_parameters : dict
            The parameters to pass to the template.

        """
        full_title = "{}/{}".format(project, title)
        page = Page(self._site, full_title, PROJECT_NAMESPACE)
        template = Template(template_name, True)
        for key, value in template_parameters.items():
            template.add_parameter(key, value)
        page.text = "{}".format(template)
        page.save(summary)

    def add_global_metrics_subpage(self, project):
        """Add a global metrics subpage under the project page.

        The title of this page is "Global Metrics". It is created by
        substituting the template "Global Metrics-sida".

        Parameters
        ----------
        project : str
            The project name.

        """
        title = "Global_Metrics"
        summary = "[TEST] Skapa undersida för global metrics."
        self._add_subpage(project, title, summary, "Global Metrics-sida")

    def add_mentions_subpage(self, project):
        """Add a mentions subpage under the project page.

        The title of this page is "Omnämnande". It is created by
        substituting the template "Omnämnande-sida".

        Parameters
        ----------
        project : str
            The project name.

        """
        title = "Omnämnande"
        summary = "[TEST] Skapa undersida för omnämnande."
        self._add_subpage(project, title, summary, "Omnämnande-sida")

    def add_project_data_subpage(
            self,
            project,
            owner,
            start,
            end,
            financier,
            budget
    ):
        """Add a project data subpage under the project page.

        The title of this page is "Projektdata". It is created by
        substituting the template "Projektdata-sida".

        Parameters
        ----------
        project : str
            The project name.
        owner : str
            Passed to template as parameter "ansvarig".
        start : str
            Passed to template as parameter "projektstart".
        end : str
            Passed to template as parameter "projektslut".
        financier : str
            Passed to template as parameter "finansiär".
        budget : str
            Passed to template as parameter "budget".

        """
        title = "Projektdata"
        summary = "[TEST] Skapa undersida för projektdata."
        parameters = {
            "ansvarig": owner,
            "projektstart": start,
            "projektslut": end,
            "finansiär": financier,
            "budget": budget
        }
        self._add_subpage(
            project,
            title,
            summary,
            "Projektdata-sida",
            parameters
        )
