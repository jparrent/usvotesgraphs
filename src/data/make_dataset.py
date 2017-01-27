# -*- coding: utf-8 -*-
import os
from pathlib import Path
import click
import logging
from dotenv import find_dotenv, load_dotenv
import glob2
import json
from collections import OrderedDict

_ROOT = str(Path(os.getcwd()).parents[1])
_RAW_DATA_PATH = os.path.join(_ROOT, 'data/raw/')
test_input_filepath = os.path.join(_RAW_DATA_PATH, '113')


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

        return self.measures_voted_on


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

    def update_congressman(self, name, congress_id, party, state, measure, vote):
        try:
            self.records[name]['votes'][measure] = vote

        except KeyError:
            record = {'congress_id': congress_id,
                      'party': party, 'state': state, 'votes': {measure: vote}}
            self.records[name] = record

    def show_records(self):
        for k, v in self.records.iteritems():
            print k, v, '\n'
            print len(v['votes']), '\n'

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
                self.update_congressman(
                    name, congress_id, party, state, measure, vote)

        if no_votes:

            for record in no_votes:

                name = record['display_name']
                congress_id = record['id']
                party = record['party']
                state = record['state']
                vote = 0
                self.update_congressman(
                    name, congress_id, party, state, measure, vote)


class Dataset:

    def __init__(self):

        pass

    # // TODO Finish the following construct function
    # now that I can access votes with voting_records[rep]['votes'][measure]

    def construct(self, measures_voted_on, voting_records):

        for rep in voting_records.keys():

            for measure in measures_voted_on:

                if voting_records[rep]['votes'][measure]:

                    pass

                else:

                    pass

        # def construct(self, measures_voted_on, voting_records):
        #     # for i in measures_voted_on:
        #     #     print i, '\n'
        #     for tup in measures_voted_on:
        #
        #         measure = tup[1]
        #
        #         for rep in voting_records.keys():
        #
        #             if
        #
        #             voting_records[rep]['votes']

        # pd.DataFrame(data=data[1:,1:],    # values
        #             index=data[1:,0],    # 1st column as index
        #               columns=data[0,1:])  # 1st row as the column names


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

    # retreive list of tuples of vote measure metadata
    measures_voted_on = congress.get_measures_voted_on()

    # retreive congressional vote dictionary
    records = congress.records
    # records.show_records()

    # create dataframe
    # rows are congress people
    # columns are measures voted on, ordered by vote_id

    # // TODO Uncomment when ready.
    # dataset = Dataset()
    # dataset.construct(measures_voted_on, records)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
