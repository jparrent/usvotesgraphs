# -*- coding: utf-8 -*-

"""
make_dataset.py
---------------------
Functions for creating a dataframe of metadata and votes per representative.
"""
import os
from pathlib import Path
import click
import logging
import glob2
import json
from collections import OrderedDict
import numpy as np
import pandas as pd


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

        self._ROOT = str(Path(os.getcwd()).parents[1])
        self._input_data_path = os.path.join(self._ROOT, 'data/raw/')
        self.session_number = session_number
        self.input_filepath = os.path.join(self._input_data_path, self.session_number)
        self.measures_voted_on = {}
        self.Records = Records()

    def get_measures_voted_on(self):
        """This function parses all .json files in ../../data/raw/ and returns
        a dict of measures voted on, sorted by the date of each measure.
        """

        for filename in glob2.iglob(self.input_filepath + '/**/*.json'):

            with open(filename) as jfile:

                data = json.load(jfile)

            if all(x in ['Present', 'Not Voting'] for x in data['votes'].keys()):
                continue

            vote_date = data['date']
            measure = data['vote_id']
            result = data['result']
            chamber = data['chamber']

            self.measures_voted_on[measure] = {
                'date': vote_date, 'result': result, 'chamber': chamber}
            yea_votes, nay_votes = self.Records.filter_abstaining_votes(data)
            self.Records.build_vote_records(yea_votes, nay_votes, measure, chamber)

        self.measures_voted_on = OrderedDict(
            sorted(self.measures_voted_on.iteritems(), key=lambda x: x[1]['date']))

        return self.measures_voted_on, self.Records._records


class Records:
    """To make it easy to construct a dataframe of votes ((1 yea, 0 nay)) per
    representative, this class is used to create records that look like this:
    records = {
        "name": {
            "congress_id",
            "party",
            "chamber",
            "state",
            "votes": {"measure": vote (1 yea, 0 nay)}
         },
    }
    """

    def __init__(self):
        self._records = {}

    def display(self):
        """Terse method used for inspecting components of the raw .jsons.
        """

        for k, v in self._records.iteritems():
            print k, v, '\n'
            print len(v['votes']), '\n'

    def update_congressman(self, name, congress_id, chamber, party, state, measure, vote):
        """This function is called by build_vote_records to construct the
        records dict per congressman.
        """

        try:
            self._records[name]['votes'][measure] = vote

        except KeyError:
            record = {'congress_id': congress_id, 'chamber': chamber,
                      'party': party, 'state': state, 'votes': {measure: vote}}
            self._records[name] = record

    def filter_abstaining_votes(self, data):
        """Given the initial raw data (.json files), this function is used to
        pass over measures where 'yea' and 'nay' votes were not cast.
        """

        try:
            yes_votes = data['votes']['Aye']
        except KeyError:
            try:
                yes_votes = data['votes']['Yea']
            except KeyError:
                yes_votes = []

        try:
            no_votes = data['votes']['No']
        except KeyError:
            try:
                no_votes = data['votes']['Nay']
            except KeyError:
                no_votes = []

        return yes_votes, no_votes

    def format_record_entry(self, measure, record, vote_cast, chamber):
        """Used in the build_vote_records method depending on vote_cast.
        """

        name = record['display_name'].split(' ')[0].strip(',').title()
        congress_id = record['id']
        party = record['party']
        state = record['state']
        vote = vote_cast
        self.update_congressman(
            name, congress_id, chamber, party, state, measure, vote)

    def build_vote_records(self, yes_votes, no_votes, measure, chamber):
        """Primary function used to build the records dict per congressman. Makes
        use of Records.update_congressman and Records.format_record_entry.
        """

        if yes_votes:

            for record in yes_votes:

                if record == "VP":
                    continue

                vote = 1
                self.format_record_entry(measure, record, vote, chamber)

        if no_votes:

            for record in no_votes:

                if record == "VP":
                    continue

                vote = 0
                self.format_record_entry(measure, record, vote, chamber)


class Dataset:
    """This class serves to deliver a pandas dataframe of vote information,
    where each row is the Congressman's name, party, state, and the span
    of votes.
    """

    def __init__(self):

        self._ROOT = str(Path(os.getcwd()).parents[1])
        self._data_path = os.path.join(self._ROOT, 'data/processed/')
        self._rows = []

    def to_file(self, session, dataframe):
        """Produces a human-readable csv file, saved in ../../data/processed/,
        to be read by ../features/build_features.py.
        """

        filehandle = '_'.join([str(session), 'dataframe.csv'])
        out_file = os.path.join(self._data_path, filehandle)
        dataframe.to_csv(out_file, encoding='utf-8')

    def construct(self, measures_voted_on, voting_records):
        """Returns pandas dataframe object with the following form:
        RepName     Party   State   Chamber     Measure1    Measure2    ...
        Smith       D       CA      s           1           0

        Note that currently a -1 is passed if a vote is not cast.
        """

        for rep in voting_records.keys():

            row = [rep, voting_records[rep]['party'], voting_records[
                rep]['state'], voting_records[rep]['chamber']]

            for measure in measures_voted_on:

                try:

                    row.append(voting_records[rep]['votes'][measure])

                except KeyError:

                    row.append(-1.0)  # row.append(np.nan)

            self._rows.append(row)

        columns = ['Name', 'Party', 'State', 'Chamber'] + measures_voted_on.keys()
        df = pd.DataFrame(data=self._rows, columns=columns)
        df = df.set_index('Name')
        return df


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).

    Finally, creates a dataframe where rows are congress people and columns are
    measures voted on, ordered by vote_id.
    """

    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    congress = Congress(session_number)
    measures_voted_on, records = congress.get_measures_voted_on()

    dataframe = Dataset().construct(measures_voted_on, records)
    Dataset().to_file(session_number, dataframe)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
