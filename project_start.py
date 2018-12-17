#! /usr/bin/env python3

import argparse
import csv
import logging
from collections import OrderedDict

from wiki import Wiki
from phab import Phab


PROJECT_ROW = 1
FIRST_PROJECT_COLUMN = 4


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
        if row[0] == "Global Metrics":
            # Stop reading when we get to the global metrics
            # section; all goals have been read at this point.
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
    string
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
    english_name = row["Engelskt projektnamn"]
    project_goals = goals[english_name]
    wiki.add_project_data_subpage(
        name,
        owner,
        start,
        end,
        financier,
        budget,
        project_goals,
        goal_fulfillments
    )


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
    wiki = Wiki()
    phab = Phab()
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "projects_file",
        help="Path to a file containing project information. The data should be tab separated values.",
        nargs=1
    )
    parser.add_argument(
        "goal_file",
        help="Path to a file containing information about project goals. The data should be tab separated values.",
        nargs=1
    )
    args = parser.parse_args()
    with open(args.goal_file[0]) as file_:
        goals_reader = csv.reader(file_, delimiter="\t")
        goals, goal_fulfillments = read_goals(goals_reader)
    with open(args.projects_file[0]) as file_:
        projects_reader = csv.DictReader(file_, delimiter="\t")
        for row in projects_reader:
            logging.info(
                "Adding project '{}'.".format(row["Svenskt projektnamn"])
            )
            phab_id, phab_name = add_phab_project(row)
            add_wiki_pages(row, phab_id, phab_name)
