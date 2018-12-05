#! /usr/bin/env python3

import argparse
import csv

from wiki import Wiki

def add_wiki_pages(row):
    """Add a project page to the wiki.

    Also adds relevant subpages.

    Parameters
    ----------
    row : dict
        Row from the TSV file containing the project information.
    """
    project = row["Svenskt projektnamn"]
    description = row["Om projektet"]
    partners = row["Partner"]
    email_prefix = row["Mejlprefix"]
    owner = row["Ansvarig"]
    start = row["Projektstart"]
    end = row["Projektslut"]
    financier = row["Finansiär"]
    budget = row["Budget"]
    wiki.add_project_page(
        project,
        description,
        partners
    )
    wiki.add_volunteer_subpage(project, email_prefix)
    wiki.add_global_metrics_subpage(project)
    wiki.add_mentions_subpage(project)
    wiki.add_project_data_subpage(
        project,
        owner,
        start,
        end,
        financier,
        budget
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs=1)
    args = parser.parse_args()
    wiki = Wiki()
    with open(args.input_file[0]) as input_file:
        reader = csv.DictReader(input_file, delimiter="\t")
        for row in reader:
            if row["Svenskt projektnamn"] != "Testar 2019":
                # TODO: Remove this when development is done.
                continue
            add_wiki_pages(row)
            # TODO: Remove this when development is done.
            break
