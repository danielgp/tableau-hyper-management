"""
TableauHyperApiExtraLogic - a Tableau Server Client wrapper

This library facilitates publishing data source to Tableau Server
"""
# package to ensure communication with Tableau Server
import tableauserverclient as tsc
# Path manager
from pathlib import Path


class TableauServerCommunicator:
    req_opts = tsc.RequestOptions(pagesize=1000)
    tableau_server = None

    def connect_to_tableau_server(self, local_logger, timmer, connection_details):
        timmer.start()
        local_logger.debug('I am about to connect to the Tableau Server with URL: '
                           + connection_details['Tableau Server'] + ' and the Site '
                           + connection_details['Tableau Site'] + ' using the Username '
                           + connection_details['Username'])
        self.tableau_server = tsc.Server(connection_details['Tableau Server'], True)
        tableau_auth = tsc.TableauAuth(connection_details['Username'],
                                       connection_details['Password'],
                                       connection_details['Tableau Site'])
        self.tableau_server.auth.sign_in(tableau_auth)
        local_logger.debug('Connection to the Tableau Server has been established successfully!')
        timmer.stop()

    def disconnect_from_tableau_server(self, local_logger, timmer):
        timmer.start()
        self.tableau_server.auth.sign_out()
        local_logger.debug('The connection to the Tableau Server has been terminated!')
        timmer.stop()

    @staticmethod
    def get_project_relevancy(relevant_projects_to_filter, filtering_type, current_project):
        relevant = 0
        if filtering_type == 'JustOnesMentioned':
            if current_project.name.replace(chr(8211), chr(45)) in relevant_projects_to_filter:
                relevant = 1
        elif filtering_type == 'OnesMentionedMarked':
            relevant = 2
        elif filtering_type == 'All':
            relevant = 99
        return relevant

    @staticmethod
    def is_publishing_possible(local_logger, relevant_project_name, relevant_project_ids):
        publish_possible = False
        int_found_projects = len(relevant_project_ids)
        if int_found_projects == 0:
            local_logger.error('No project with provided name "' + relevant_project_name
                               + '" has been found')
            local_logger.debug('No publishing action will take place!')
            local_logger.debug('Check your input parameter values for accuracy and try again!')
        elif int_found_projects > 1:
            local_logger.error(f'There are {str(int_found_projects)} projects with provided name "'
                               + relevant_project_name + ' but a unique identifier is expected')
            local_logger.debug('No publishing action will take place!')
            local_logger.info('Check your input parameter values for accuracy and try again!')
        else:
            publish_possible = True
            local_logger.info(f'A single project identifier was found "' + relevant_project_ids[0]
                              + '" so I will proceed with publishing provided file there')
            local_logger.info('Stay tuned for the confirmation')
        return publish_possible

    def load_tableau_project_ids(self, local_logger, timmer, relevant_projects_to_filter,
                                 str_filtering_type):
        timmer.start()
        project_items, pagination_item = self.tableau_server.projects.get(req_options=self.req_opts)
        local_logger.info('Reading list of all projects available has been completed')
        local_logger.info(str(len(project_items)) + ' projects were found')
        timmer.stop()
        timmer.start()
        dictionary_project_ids = []
        project_counter = 0
        for project_current in project_items:
            relevant = self.get_project_relevancy(relevant_projects_to_filter,
                                                  str_filtering_type,
                                                  project_current)
            if relevant >= 1:
                dictionary_project_ids.append(project_counter)
                dictionary_project_ids[project_counter] = project_current.id
                project_counter = project_counter + 1
        local_logger.info('Retaining the projects according to filtering type provided ("'
                          + str_filtering_type + '") has been completed')
        local_logger.info(str(len(dictionary_project_ids)) + ' projects were retained')
        timmer.stop()
        return dictionary_project_ids

    def publish_data_source_to_tableau_server(self, local_logger, timmer, publish_details):
        timmer.start()
        local_logger.info('About to start publishing')
        data_source_name = Path(publish_details['Tableau Extract File']).name\
            .replace('.hyper', '') + " Extract"
        project_data_source = tsc.DatasourceItem(publish_details['Project ID'], data_source_name)
        self.tableau_server.datasources.publish(project_data_source,
                                                publish_details['Tableau Extract File'],
                                                publish_details['Publishing Mode'])
        local_logger.info('Publishing has finished with success!')
        timmer.stop()
