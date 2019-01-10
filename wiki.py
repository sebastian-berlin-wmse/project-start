from collections import OrderedDict
import logging

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
    _dry_run : bool
        If True, no data is written to the wiki.
    """

    def __init__(self, dry_run):
        self._dry_run = dry_run
        self._site = Site()

    def add_project_page(
            self,
            name,
            description,
            partners,
            phab_id,
            phab_name
    ):
        """Add the main project page.

        Parameters
        ----------
        name : str
            The project name in Swedish. This will be used as title
            for the page.
        description : str
            Passed to template as parameter "beskrivning".
        partners : str
            Passed to template as parameter "samarbetspartners".

        """
        page = Page(self._site, name, PROJECT_NAMESPACE)
        if page.exists():
            logging.warning(
                "Project page '{}' already exists. It will not be created.".format(page.title())  # noqa: E501
            )
        else:
            template = Template("Projekt-sida", True)
            template.add_parameter("beskrivning", description)
            pratner_bullet_list = self._create_partner_bullet_list(partners)
            template.add_parameter("samarbetspartners", pratner_bullet_list)
            template.add_parameter("phabricatorId", phab_id)
            template.add_parameter("phabricatorName", phab_name)
            content = "{}".format(template)
            page.text = content
            logging.debug("Writing to project page '{}'".format(page.title()))
            logging.debug(page.text)
            if not self._dry_run:
                page.save("Skapa projektsida.")

    def _create_partner_bullet_list(self, partners_string):
        """Create a wikitext bullet list of partners.

        Parameters
        ----------
        partners_string : str
            Comma separated partner names.

        Returns
        -------
        str
            The empty string if the input is empty, else a wikitext
            bullet list with the partners.

        """
        if partners_string == "":
            return ""
        partners = partners_string.split(", ")
        bullet_list_string = "\n".join(["* {}".format(p) for p in partners])
        return bullet_list_string

    def add_volunteer_subpage(self, project, email_prefix):
        """Add a volunteer subpage under the project page.

        The title of this page is "Frivillig". It is created by
        substituting the template "Frivillig-sida".

        Parameters
        ----------
        project : str
            The project name in Swedish.
        email_prefix : str
            Passed to template as parameter "e-post_prefix".

        """
        title = "Frivillig"
        summary = "Skapa undersida för frivilliga."
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
            template_parameters=None
    ):
        """Add a  subpage under the project page.

        Parameters
        ----------
        project : str
            The project name in Swedish.
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
        if page.exists():
            logging.warning(
                "Subpage '{}' already exists. It will not be created.".format(
                    page.title()
                )
            )
        else:
            template = Template(template_name, True)
            if template_parameters:
                for key, value in template_parameters.items():
                    template.add_parameter(key, value)
            page.text = "{}".format(template.multiline_string())
            logging.debug("Writing to subpage '{}'.".format(page.title()))
            logging.debug(page.text)
            if not self._dry_run:
                page.save(summary)

    def add_global_metrics_subpage(self, project):
        """Add a global metrics subpage under the project page.

        The title of this page is "Global Metrics". It is created by
        substituting the template "Global Metrics-sida".

        Parameters
        ----------
        project : str
            The project name in Swedish.

        """
        title = "Global_Metrics"
        summary = "Skapa undersida för global metrics."
        self._add_subpage(project, title, summary, "Global Metrics-sida")

    def add_mentions_subpage(self, project):
        """Add a mentions subpage under the project page.

        The title of this page is "Omnämnande". It is created by
        substituting the template "Omnämnande-sida".

        Parameters
        ----------
        project : str
            The project name in Swedish.

        """
        title = "Omnämnande"
        summary = "Skapa undersida för omnämnande."
        self._add_subpage(project, title, summary, "Omnämnande-sida")

    def add_project_data_subpage(
            self,
            project,
            owner,
            start,
            end,
            financier,
            budget,
            financier_2,
            budget_2,
            goals,
            goal_fulfillments
    ):
        """Add a project data subpage under the project page.

        The title of this page is "Projektdata". It is created by
        substituting the template "Projektdata-sida".

        Parameters
        ----------
        project : str
            The project name in Swedish.
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
        financier_2 : str
            Passed to template as parameter "finansiär_2".
        budget_2 : str
            Passed to template as parameter "budget_2".
        goals : OrderedDict
            A map of goal names and planned values for this project.
        goals : dict
            A map of goal names and fulfillment texts.

        """
        title = "Projektdata"
        summary = "Skapa undersida för projektdata."
        parameters = OrderedDict()
        parameters["ansvarig"] = owner
        parameters["projektstart"] = start
        parameters["projektslut"] = end
        parameters["finansiär"] = financier
        parameters["budget"] = budget
        parameters["finansiär_2"] = financier_2
        parameters["budget_2"] = budget_2
        parameters["interna_mål"] = \
            Template("Måltexter 2018", parameters=goals)
        parameters["måluppfyllnad"] = \
            self._create_goal_fulfillment_text(goals.keys(), goal_fulfillments)
        self._add_subpage(
            project,
            title,
            summary,
            "Projektdata-sida",
            parameters
        )

    def _create_goal_fulfillment_text(self, goals, fulfillments):
        """Create a string with the fulfillment texts for a set of goals.

        Parameters
        ----------
        goals : list
            Goal names for which to add fulfillments.
        fulfillments : dict
            Map of goal names and fulfillment texts.

        Returns
        -------
        str
            Contains one fulfillment text as a wikitext list.
        """
        fulfillment_text = ""
        for goal in goals:
            fulfillment_text += "\n* {}".format(fulfillments[goal])
        return fulfillment_text

    def add_categories(self, project, year, area):
        """Add categories to the project's category page.

        Adds the project category to categories for year and area, if
        given.

        Parameters
        ----------
        project : str
            The project name in Swedish.
        year : int
            The year category to add the project category to.
        area : str
            The area category to add the project category to. If the
            empty string, no area category is added.
        """
        year_category = "Projekt {}".format(year)
        page = Page(self._site, project, "Kategori")
        if page.exists():
            logging.warning(
                "Category page '{}' already exists. It will not be created.".format(page.title())  # noqa: E501
            )
        else:
            page.text = "[[Kategori:{}]]".format(year_category)
            if area:
                page.text += "\n[[Kategori:{}]]".format(area)
            logging.debug("Writing to category page '{}'".format(page.title()))
            logging.debug(page.text)
            if not self._dry_run:
                page.save("Skapa projektkategori.")
