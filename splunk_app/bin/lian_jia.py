#
# Copyright 2013 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys, urllib2, json, logging, os
import psycopg2

from splunklib.modularinput import *
from splunk.clilib.bundle_paths import make_splunkhome_path
from logging.handlers import RotatingFileHandler

maxbytes = 20000000

def get_logger(logger_id):
    log_path = make_splunkhome_path(["var", "log", "lianjia_analysis"])
    if not (os.path.isdir(log_path)):
        os.makedirs(log_path)

    handler = RotatingFileHandler(log_path + '/lianjia_analysis.log', maxBytes=maxbytes,
                                    backupCount=20)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_id)
    logger.setLevel(logging.INFO)

    logger.addHandler(handler)
    return logger

logger = get_logger("FA_SETUP")

class MyScript(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, the validate_input function.
    """
    def get_scheme(self):
        """When Splunk starts, it looks for all the modular inputs defined by
        its configuration, and tries to run them with the argument --scheme.
        Splunkd expects the modular inputs to print a description of the
        input in XML on stdout. The modular input framework takes care of all
        the details of formatting XML and printing it. The user need only
        override get_scheme and return a new Scheme object.

        :return: scheme, a Scheme object
        """
        # Splunk will display "Github Repository Forks" to users for this input
        scheme = Scheme("Lian Jia Houses")

        scheme.description = "Streams events giving the number of data from Lian Jia."
        # If you set external validation to True, without overriding validate_input,
        # the script will accept anything as valid. Generally you only need external
        # validation if there are relationships you must maintain among the
        # parameters, such as requiring min to be less than max in this example,
        # or you need to check that some resource is reachable or valid.
        # Otherwise, Splunk lets you specify a validation string for each argument
        # and will run validation internally using that string.
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        host_argument = Argument("dbhost")
        host_argument.title = "Database Host"
        host_argument.data_type = Argument.data_type_string
        host_argument.description = "The host for the lian jia database"
        host_argument.required_on_create = True
        # If you are not using external validation, you would add something like:
        #
        # scheme.validation = "host==splunk"
        scheme.add_argument(host_argument)

        database_argument = Argument("database")
        database_argument.title = "Data Base"
        database_argument.data_type = Argument.data_type_string
        database_argument.description = "Name of the Data Base."
        database_argument.required_on_create = True
        scheme.add_argument(database_argument)

        user_argument = Argument("user")
        user_argument.title = "User Name"
        user_argument.data_type = Argument.data_type_string
        user_argument.description = "Name of the user."
        user_argument.required_on_create = True
        scheme.add_argument(user_argument)

        return scheme

    def validate_input(self, validation_definition):
        """In this example we are using external validation to verify that the Github
        repository exists. If validate_input does not raise an Exception, the input
        is assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.

        When using external validation, after splunkd calls the modular input with
        --scheme to get a scheme, it calls it again with --validate-arguments for
        each instance of the modular input in its configuration files, feeding XML
        on stdin to the modular input to do validation. It is called the same way
        whenever a modular input's configuration is edited.

        :param validation_definition: a ValidationDefinition object
        """
        pass

    def get_name_by_id(self, arrs, idn, rn):
        for arr in arrs:
            if arr[0] == idn:
                return arr[rn]
        return ''
    

    def stream_events(self, inputs, ew):
        """This function handles all the action: splunk calls this modular input
        without arguments, streams XML describing the inputs to stdin, and waits
        for XML on stdout describing events.

        If you set use_single_instance to True on the scheme in get_scheme, it
        will pass all the instances of this input to a single instance of this
        script.

        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """
        # Go through each input for this modular input
        conn = None
        logger.info("start stream event")
        for input_name, input_item in inputs.inputs.iteritems():
            # Get fields from the InputDefinition object
            dbhost = input_item["dbhost"]
            database = input_item["database"]
            user = input_item["user"]
            try:
                conn = psycopg2.connect(host=dbhost, database=database, user=user)
                logger.info("kekeda!")
                cur = conn.cursor()
                # get info for communities
                cur.execute('SELECT * FROM communities')
                comms = cur.fetchall()
                cur.execute('SELECT * FROM biz_circles')
                bcles = cur.fetchall()
                cur.execute('SELECT * FROM districts')
                dists = cur.fetchall()
                cur.execute('SELECT * FROM cities')
                cities = cur.fetchall()
                cur.close()
                
                for row in comms:
                    # Create an Event object, and set its fields
                    event = Event()
                    event.stanza = input_name
                    event.data = ("id={},city_name={},district_name={},"
                                    "biz_circle_name={},name={},building_finish_year={},"
                                    "building_type={},second_hand_quantity={},second_hand_unit_price={},"
                                    "updated_at={},page_fetched_at={},".format(row[0],self.get_name_by_id(cities, row[1], 1), \
                                                self.get_name_by_id(dists, row[2], 2), self.get_name_by_id(bcles, row[3], 3), \
                                                row[4], row[5], row[6], row[7], row[8], row[10], row[11]))
                    if row[9]:
                        for k, v in row[9].items():
                            if v:
                                event.data += k + '=' + v + ','
                            else:
                                event.data += k + '=--,'
                    # Tell the EventWriter to write this event
                    ew.write_event(event)
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error("cuo zai: {}".format(error))
            finally:
                if conn is not None:
                    conn.close()

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))