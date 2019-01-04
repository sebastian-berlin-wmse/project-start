#! /usr/bin/env python3

import argparse
import csv
import logging
from collections import OrderedDict
import datetime

from wiki import Wiki
from phab import Phab


PROJECT_ROW = 1
FIRST_PROJECT_COLUMN = 4
LAST_PROJECT_COLUMN = 56


def read_goals(tsv):
    """Read goal values from tab separated data.

    Parameters
    ----------
    tsv : iterator
        Gives one list per row from tab separated data.

    Returns
    -------
    dict
        Map of project names to dicts that maps goal name to planned
        value.
    dict
        Map of goal names to goal fulfillment texts.
    """
    goals = OrderedDict()
    fulfillments = {}
    for i, row in enumerate(tsv):
        if i == LAST_PROJECT_COLUMN:
            # Stop reading when we all projects have been read.
            break
        elif row[0] == "":
            # Skip rows that have nothing in the first field; they
            # will not contain any goal numbers.
            continue
        description = row[0]
        name = get_goal_name(description)
        fulfillment = row[1]
        if fulfillment:
            fulfillments[name] = fulfillment
        for j, field in enumerate(row):
            if j >= FIRST_PROJECT_COLUMN:
                if i == PROJECT_ROW:
                    # Add keys for all of the projects. Since we
                    # use an ordered dictionary, this allows us to
                    # find the correct project when we add goal
                    # values.
                    project = field
                    if project == "":
                        # Temporarily add empty columns to maintain
                        # the indices.
                        goals[j] = None
                    else:
                        # Use ordered dictionary here to keep the
                        # order of the goals when they are added to
                        # the template.
                        goals[project] = OrderedDict()
                elif i > PROJECT_ROW:
                    planned_value = field
                    project_index = j - FIRST_PROJECT_COLUMN
                    project_name = list(goals.keys())[project_index]
                    if planned_value:
                        goals[project_name][name] = planned_value
    # Remove any empty columns.
    goals = {k: v for k, v in goals.items() if v}
    # Make it a normal dictionary, since we don't need to keep track
    # of project indices anymore.
    return dict(goals), fulfillments


def get_goal_name(description):
    """Get goal name from description.

    Parameters
    ----------
    description : string
        Goal description in the format "T.1.1 - Berika projekten med
        25 nya resurser".

    Returns
    -------
    str
        Goal name in the format "T.1.1".
    """
    return description.split(" - ")[0]


def add_wiki_pages(row, phab_id, phab_name):
    """Add a project page to the wiki.

    Also adds relevant subpages.

    Parameters
    ----------
    row : dict
        Row from the TSV file containing the project information.
    phab_id : int
        Id of the project on Phabricator.
    phab_name : str
        Name of the project on Phabricator
    """
    logging.info("Adding wiki pages.")
    name = row["Svenskt projektnamn"]
    description = row["Om projektet"]
    partners = row["Partner"]
    wiki.add_project_page(
        name,
        description,
        partners,
        phab_id,
        phab_name
    )
    email_prefix = row["Mejlprefix"]
    wiki.add_volunteer_subpage(name, email_prefix)
    wiki.add_global_metrics_subpage(name)
    wiki.add_mentions_subpage(name)
    owner = row["Ansvarig"]
    start = row["Projektstart"]
    end = row["Projektslut"]
    financier = row["Finansiär"]
    budget = row["Budget"]
    financier_2 = row["Finansiär 2"]
    budget_2 = row["Budget 2"]
    english_name = row["Engelskt projektnamn"]
    project_goals = goals[english_name]
    wiki.add_project_data_subpage(
        name,
        owner,
        start,
        end,
        financier,
        budget,
        financier_2,
        budget_2,
        project_goals,
        goal_fulfillments
    )
    if args.year:
        year = args.year
    else:
        year = datetime.date.today().year
    area = row["Område"]
    wiki.add_categories(name, year, area)


def add_phab_project(row):
    """Add a project on Phabricator.

    Parameters
    ----------
    row : dict
        Row from the TSV file containing the project information.
    """
    logging.info("Adding Phabricator project.")
    name = row["Engelskt projektnamn"]
    description = row["About the project"]
    return phab.add_project(name, description)

if __name__ == "__main__":
    logging_format = "%(asctime)s[%(levelname)s](%(module)s): %(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        format=logging_format,
        filename="project-start.log"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(
        logging.Formatter(logging_format)
    )
    logging.getLogger().addHandler(stream_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year",
        "-y",
        help="Year for the projects created. If not given, the current year will be used."  # noqa: E501
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        help="Don't write anything to the target platforms.",
        action="store_true"
    )
    parser.add_argument(
        "projects_file",
        help="Path to a file containing project information. The data should be tab separated values.",  # noqa: E501
        nargs=1
    )
    parser.add_argument(
        "goal_file",
        help="Path to a file containing information about project goals. The data should be tab separated values.",  # noqa: E501
        nargs=1
    )
    args = parser.parse_args()
    logging.debug("Creating projects.")
    wiki = Wiki(args.dry_run)
    phab = Phab(args.dry_run)
    with open(args.goal_file[0]) as file_:
        goals_reader = csv.reader(file_, delimiter="\t")
        goals, goal_fulfillments = read_goals(goals_reader)
    with open(args.projects_file[0]) as file_:
        projects_reader = csv.DictReader(file_, delimiter="\t")
        for row in projects_reader:
            superproject = row["Överprojekt"]
            project_name = row["Engelskt projektnamn"]
            if superproject:
                # Don't add anything for subprojects.
                continue
            if project_name not in goals:
                logging.warn(
                    "Project name '{}' found in projects file, but not in goals file. It will not be created.".format(project_name)  # noqa: E501
                )
                continue
            logging.info(
                "Adding project '{}'.".format(row["Svenskt projektnamn"])
            )
            phab_id, phab_name = add_phab_project(row)
            add_wiki_pages(row, phab_id, phab_name)
            goals[project_name]["added"] = True
    for project, parameters in goals.items():
        if "added" not in parameters:
            logging.warn(
                "Project name '{}' found in goals file, but not in projects file. It will not be created.".format(project)  # noqa: E501
            )
