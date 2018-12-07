#! /usr/bin/env python3

import argparse
import csv
import logging

from wiki import Wiki
from phab import Phab


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
    wiki = Wiki()
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
    wiki.add_project_data_subpage(
        name,
        owner,
        start,
        end,
        financier,
        budget
    )


def add_phab_project(row):
    """Add a project on Phabricator.

    Parameters
    ----------
    row : dict
        Row from the TSV file containing the project information.
    """
    logging.info("Adding Phabricator project.")
    phab = Phab()
    name = row["Engelskt projektnamn"]
    description = row["About the project"]
    return phab.add_project(name, description)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs=1)
    args = parser.parse_args()
    with open(args.input_file[0]) as input_file:
        reader = csv.DictReader(input_file, delimiter="\t")
        for row in reader:
            logging.info(
                "Adding project '{}'.".format(row["Svenskt projektnamn"])
            )
            phab_id, phab_name = add_phab_project(row)
            add_wiki_pages(row, phab_id, phab_name)
