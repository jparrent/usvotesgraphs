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


class Congress:

    def __init__(self, session_number):

        self.session_number = session_number
        self.input_filepath = os.path.join(_RAW_DATA_PATH, self.session_number)
        self.measures_voted_on = []
        self.records = Records()

    def filter_abstaining_votes(self, data):

        if all(x in ['Present', 'Not Voting'] for x in data['votes'].keys()):
            pass

        try:
            yes_votes = data['votes']['Aye']
        except KeyError:
            try:
                yes_votes = data['votes']['Yea']
            except KeyError:
                pass
                yes_votes = []

        try:
            no_votes = data['votes']['No']
        except KeyError:
            try:
                no_votes = data['votes']['Nay']
            except KeyError:
                pass
                no_votes = []

        return yes_votes, no_votes

    def build_vote_records(self, yes_votes, no_votes, measure):

        if yes_votes:

            for record in yes_votes:

                name = record['display_name']
                congress_id = record['id']
                party = record['party']
                state = record['state']
                vote = 1
                self.records.update_congressman(
                    name, congress_id, party, state, measure, vote)

        if no_votes:

            for record in no_votes:

                name = record['display_name']
                congress_id = record['id']
                party = record['party']
                state = record['state']
                vote = 0
                self.records.update_congressman(
                    name, congress_id, party, state, measure, vote)

    def get_measures_voted_on(self):

        for filename in glob2.iglob(self.input_filepath + '/**/*.json'):

            with open(filename) as jfile:

                data = json.load(jfile)

            vote_date = data['date']
            measure = data['vote_id']
            result = data['result']

            self.measures_voted_on.append((vote_date, measure, result))

            yea_votes, nay_votes = self.filter_abstaining_votes(data)

            self.build_vote_records(yea_votes, nay_votes, measure)

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

    def show_records(self):
        for k, v in self.records.iteritems():
            print k, v, '\n'
            print len(v['votes']), '\n'


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
    congress.records.show_records()

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
