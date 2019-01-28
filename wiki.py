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
    _config : dict
        Parameters read from configuration file.
    _site : Site
        `Site` object used by Pywikibot
    _dry_run : bool
        If True, no data is written to the wiki.
    """

    def __init__(self, config, dry_run, overwrite):
        self._site = Site()
        self._config = config
        self._dry_run = dry_run
        self._overwrite = overwrite

    def add_project_page(
            self,
            phab_id,
            phab_name,
            parameters,
            goals,
            goal_fulfillments
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
        name = parameters[self._config["name"]]
        page = Page(self._site, name, PROJECT_NAMESPACE)
        if page.exists() and not self._overwrite:
            logging.warning(
                "Project page '{}' already exists. It will not be created.".format(page.title())  # noqa: E501
            )
        else:
            template = Template(self._config["project_template"], True)
            project_parameters = self._config["project_parameters"].items()
            for template_parameter, label in project_parameters:
                template.add_parameter(template_parameter, parameters[label])
            template.add_parameter("phabricatorId", phab_id)
            template.add_parameter("phabricatorName", phab_name)
            content = "{}".format(template)
            page.text = content
            logging.info("Writing to project page '{}'".format(page.title()))
            logging.debug(page.text)
            if not self._dry_run:
                page.save()
            for subpage in self._config["subpages"]:
                subpage_parameters = {}
                if "parameters" in subpage:
                    for key, value in subpage["parameters"].items():
                        subpage_parameters[key] = parameters[value]
                if "add_goals_parameters" in subpage:
                    # Special case for goals parameters, as they are not
                    # just copied.
                    print(subpage["add_goals_parameters"].values())
                    template_key = \
                        list(subpage["add_goals_parameters"].keys())[0]
                    template_value = \
                        subpage["add_goals_parameters"][template_key]
                    subpage_parameters[template_key] = \
                        Template(template_value, parameters=goals)
                    subpage_parameters["måluppfyllnad"] = \
                        self._create_goal_fulfillment_text(
                            goals.keys(),
                            goal_fulfillments
                        )
                self._add_subpage(
                    name,
                    subpage["title"],
                    subpage["template_name"],
                    subpage_parameters
                )

    def _add_subpage(
            self,
            project,
            title,
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
        if page.exists() and not self._overwrite:
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
            logging.info("Writing to subpage '{}'.".format(page.title()))
            logging.debug(page.text)
            if not self._dry_run:
                page.save()

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
        if page.exists() and not self._overwrite:
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
