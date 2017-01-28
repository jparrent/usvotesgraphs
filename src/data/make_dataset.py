# -*- coding: utf-8 -*-
import os
from pathlib import Path
import click
import logging
import glob2
import json
from collections import OrderedDict
import numpy as np
import pandas as pd
# from dotenv import find_dotenv, load_dotenv


_ROOT = str(Path(os.getcwd()).parents[1])
_RAW_DATA_PATH = os.path.join(_ROOT, 'data/raw/')
_PROCESSED_DATA_PATH = os.path.join(_ROOT, 'data/processed/')


class Congress:
    """This class is used to build a dictionary of measures that have been
    voted on for a given congressional session:
    measures_voted_on = {
        "measure": {
            "date",
            "result"
         },
    }

    """

    def __init__(self, session_number):

        self.session_number = session_number
        self.input_filepath = os.path.join(_RAW_DATA_PATH, self.session_number)
        self.measures_voted_on = {}
        self.records = Records()

    def get_measures_voted_on(self):

        for filename in glob2.iglob(self.input_filepath + '/**/*.json'):

            with open(filename) as jfile:

                data = json.load(jfile)

            vote_date = data['date']
            measure = data['vote_id']
            result = data['result']

            self.measures_voted_on[measure] = {'date': vote_date, 'result': result}
            yea_votes, nay_votes = self.records.filter_abstaining_votes(data)
            self.records.build_vote_records(yea_votes, nay_votes, measure)

        self.measures_voted_on = OrderedDict(
            sorted(self.measures_voted_on.iteritems(), key=lambda x: x[1]['date']))

        return self.measures_voted_on, self.records.records


class Records:
    """To make it easy to construct a dataframe of votes ((1 yea, 0 nay)) per
    representative, this class is used to create records that look like this:
    records = {
        "name": {
            "congress_id",
            "party",
            "state"
            "votes": {"measure": vote (1 yea, 0 nay)}
         },
    }
    """

    def __init__(self):
        self.records = {}

    def show_records(self):
        for k, v in self.records.iteritems():
            print k, v, '\n'
            print len(v['votes']), '\n'

    def update_congressman(self, name, congress_id, party, state, measure, vote):
        try:
            self.records[name]['votes'][measure] = vote

        except KeyError:
            record = {'congress_id': congress_id,
                      'party': party, 'state': state, 'votes': {measure: vote}}
            self.records[name] = record

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

                name = record['display_name'].split(' ')[0].strip(',')
                congress_id = record['id']
                party = record['party']
                state = record['state']
                vote = 1
                self.update_congressman(
                    name, congress_id, party, state, measure, vote)

        if no_votes:

            for record in no_votes:

                name = record['display_name'].split(' ')[0].strip(',')
                congress_id = record['id']
                party = record['party']
                state = record['state']
                vote = 0
                self.update_congressman(
                    name, congress_id, party, state, measure, vote)


class Dataset:
    """This class serves to deliver a pandas dataframe of vote information,
    where each row is the Congressman's name, party, state, and the span
    of votes.
    """

    def __init__(self):

        self.rows = []

    def output_to_file(self, session, dataframe):

        filehandle = '_'.join([str(session), 'dataframe.csv'])
        out_file = os.path.join(_PROCESSED_DATA_PATH, filehandle)
        dataframe.to_csv(out_file, encoding='utf-8')

    def construct(self, measures_voted_on, voting_records):

        for rep in voting_records.keys():

            row = [rep, voting_records[rep]['party'], voting_records[rep]['state']]

            for measure in measures_voted_on:

                try:

                    row.append(voting_records[rep]['votes'][measure])

                except KeyError:

                    # row.append(np.nan)
                    row.append(-1.0)

            self.rows.append(row)

        columns = ['Name', 'Party', 'State'] + measures_voted_on.keys()
        df = pd.DataFrame(data=self.rows, columns=columns)
        df = df.set_index('Name')
        return df


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # create congress for a given session, e.g., 113th congress
    congress = Congress(session_number)

    # retreive vote/measure metadata and Congressional records
    measures_voted_on, records = congress.get_measures_voted_on()

    """Create a dataframe where rows are congress people and columns are
    measures voted on, ordered by vote_id.
    """
    dataframe = Dataset().construct(measures_voted_on, records)
    Dataset().output_to_file(session_number, dataframe)
    print dataframe.head()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
