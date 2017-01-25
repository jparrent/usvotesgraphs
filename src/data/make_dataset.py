# -*- coding: utf-8 -*-
import os
from pathlib import Path
import click
import logging
from dotenv import find_dotenv, load_dotenv
import glob2
import json

_ROOT = str(Path(os.getcwd()).parents[1])
_RAW_DATA_PATH = os.path.join(_ROOT, 'data/raw/')
test_input_filepath = os.path.join(_RAW_DATA_PATH, '113')


class Congress(list):

    def __init__(self, session_number):

        self.session_number = session_number
        self.input_filepath = os.path.join(_RAW_DATA_PATH, self.session_number)
        self.measures_voted_on = []
        self.records = Records()

    def get_measures_voted_on(self):

        for filename in glob2.iglob(self.input_filepath + '/**/*.json'):

            with open(filename) as jfile:

                data = json.load(jfile)

            vote_date = data['date']
            measure = data['vote_id']
            result = data['result']

            self.measures_voted_on.append((vote_date, measure, result))

            if all(x in ['Present', 'Not Voting'] for x in data['votes'].keys()):
                continue
            print data['votes'].keys()
            try:
                yea_votes = data['votes']['Aye']
            except KeyError:
                try:
                    yea_votes = data['votes']['Yea']
                except KeyError:
                    continue

            try:
                nay_votes = data['votes']['No']
            except KeyError:
                try:
                    nay_votes = data['votes']['Nay']
                except KeyError:
                    continue

            if yea_votes:

                for record in nay_votes:

                    name = record['display_name']
                    congress_id = record['id']
                    party = record['party']
                    state = record['state']
                    vote = 1
                    self.records.update_congressman(
                        name, congress_id, party, state, measure, vote)

            if nay_votes:

                for record in nay_votes:

                    name = record['display_name']
                    congress_id = record['id']
                    party = record['party']
                    state = record['state']
                    vote = 0
                    self.records.update_congressman(
                        name, congress_id, party, state, measure, vote)

        self.measures_voted_on.sort(key=lambda tup: tup[0])

        return self.measures_voted_on


class Records:

    def __init__(self):
        self.records = {}

    def update_congressman(self, name, congress_id, party, state, measure, vote):
        try:
            self.records[name]['votes'].append((measure, vote))

        except KeyError:
            record = {"congress_id": congress_id,
                      "party": party, "state": state, "votes": [(measure, vote)]}
            self.records[name] = record


# class Congressman(dict):
#
#     def __init__(self, name, congress_id, party, state):
#
#         self.name = name
#         self.id = congress_id
#         self.party = party
#         self.measures_voted_on = []
#
#     def add_vote(self, measure, vote):
#
#         self.measures_voted_on.append((measure, vote))
#
#     def get_votes(self):
#
#         self.measures_voted_on.sort(key=lambda tup: tup[0])
#
#         return self.measures_voted_on

    # def get_votes(self, data):
    #     vote_id = data['vote_id']
    #     votes_yay = data['votes']['Aye']
    #     votes_nay = data['votes']['No']


@click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
@click.argument('session_number')
def main(session_number):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # initialize some variables and dataframes

    # parse raw/ data directory
    congress = Congress(session_number)
    measures_voted_on = congress.get_measures_voted_on()

    # create dataframe
    # rows are congress people
    # columns are measures voted on, ordered by vote_id


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
