"""
TableauServerCommunication - a Tableau Server Client wrapper

This library facilitates publishing data source to Tableau Server
"""
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os
# package to ensure communication with Tableau Server
import tableauserverclient
# Path manager
from pathlib import Path


class TableauServerCommunicator:
    req_opts = tableauserverclient.RequestOptions(pagesize=1000)
    tableau_server = None
    locale = None

    def __init__(self, in_language):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(
            locale_domain, localedir=locale_folder, languages=[in_language], fallback=True)

    def connect_to_tableau_server(self, local_logger, timer, in_connection):
        timer.start()
        local_logger.debug(self.locale.gettext(
            'About to connect to the Tableau Server with URL: {tableau_server}, '
            + 'Site {tableau_site} with Username = {user_name}')
                           .replace('{tableau_server}', in_connection['Tableau Server'])
                           .replace('{tableau_site}', in_connection['Tableau Site'])
                           .replace('{user_name}', in_connection['Username']))
        self.tableau_server = tableauserverclient.Server(in_connection['Tableau Server'], True)
        tableau_auth = tableauserverclient.TableauAuth(
            in_connection['Username'], in_connection['Password'], in_connection['Tableau Site'])
        self.tableau_server.auth.sign_in(tableau_auth)
        local_logger.debug(self.locale.gettext(
            'Connection to the Tableau Server has been established successfully!'))
        timer.stop()

    def disconnect_from_tableau_server(self, local_logger, timer):
        timer.start()
        self.tableau_server.auth.sign_out()
        local_logger.debug(self.locale.gettext(
            'Connection to the Tableau Server has been terminated!'))
        timer.stop()

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

    def is_publishing_possible(self, local_logger, relevant_project_name, relevant_project_ids):
        publish_possible = False
        int_found_projects = len(relevant_project_ids)
        if int_found_projects == 0:
            local_logger.error(self.locale.gettext(
                'No project with provided name "{project_name}" has been found')
                               .replace('{project_name}', relevant_project_name))
            self.no_publishing_feedback()
        elif int_found_projects > 1:
            local_logger.error(self.locale.gettext(
                'There are {projects_counted} projects with provided name "'
                + '{project_name}" but a unique identifier is expected')
                               .replace('{projects_counted}', str(int_found_projects))
                               .replace('{project_name}', relevant_project_name))
            self.no_publishing_feedback()
        else:
            publish_possible = True
            local_logger.info(self.locale.gettext(
                'A single project identifier was found "{project_guid}", '
                + 'so I will proceed with publishing provided file there')
                               .replace('{project_guid}', relevant_project_ids[0]))
            local_logger.info(self.locale.gettext('Stay tuned for the confirmation'))
        return publish_possible

    def load_tableau_project_ids(self, local_logger, timer, in_projects_to_filter, in_filter_type):
        timer.start()
        project_items, pagination_item = self.tableau_server.projects.get(req_options=self.req_opts)
        local_logger.info(self.locale.gettext(
            'Reading list of all projects available has been completed'))
        local_logger.info(self.locale.gettext(
            'A number of {projects_counted} projects have been identified')
                          .replace('{projects_counted}', str(len(project_items))))
        timer.stop()
        timer.start()
        dictionary_project_ids = []
        project_counter = 0
        for project_current in project_items:
            relevant = self.get_project_relevancy(
                in_projects_to_filter, in_filter_type, project_current)
            if relevant >= 1:
                dictionary_project_ids.append(project_counter)
                dictionary_project_ids[project_counter] = project_current.id
                project_counter = project_counter + 1
        local_logger.info(self.locale.gettext(
            'Retaining the projects according to filtering type provided ({filter_type}) '
            + 'has been completed')
                          .replace('{filter_type}', in_filter_type))
        local_logger.info(self.locale.gettext(
            'A number of {projects_counted} projects have been identified')
                          .replace('{projects_counted}', str(len(dictionary_project_ids))))
        timer.stop()
        return dictionary_project_ids

    def load_tableau_workbooks(self, relevant_project_ids_to_filter):
        all_workbooks, pagination_item = self.tableau_server.workbooks.get(
            req_options=self.req_opts)
        dictionary_workbooks = []
        workbook_counter = 0
        download_dir = 'D:\\www\\Data\\HoneywellTableauServer\\'
        for workbook_current in all_workbooks:
            if workbook_current.project_id in relevant_project_ids_to_filter:
                workbook_name = workbook_current.name
                workbook_name_standardized = workbook_name\
                    .replace('\n', ' ').replace('\r', '').replace('\\', '')
                workbook_created = workbook_current.created_at
                workbook_updated = workbook_current.updated_at
                dictionary_workbooks.append(workbook_counter)
                dictionary_workbooks[workbook_counter] = {
                    'WorkBookId': workbook_current.id,
                    'WorkBookProjectId': workbook_current.project_id,
                    'WorkBookName': workbook_name_standardized,
                    'WorkBookOwnerId': workbook_current.owner_id,
                    #'WorkBookOwnerEmail': self.tableau_server.users.get_by_id(
                    #    workbook_current.owner_id).email,
                    'WorkBookContentUrl': workbook_current.content_url,
                    'WorkBookCreatedAtUtc': workbook_created.strftime("%Y-%m-%d %H:%M:%S"),
                    'WorkBookUpdatedAtUtc': workbook_updated.strftime("%Y-%m-%d %H:%M:%S")
                }
                if workbook_name_standardized == 'SPS OTTR Tableau v3':
                    self.tableau_server.workbooks.download(
                        workbook_current.id, filepath='C:\\www\\Data\\HoneywellTableauServer',
                        include_extract=None)
                workbook_counter = workbook_counter + 1
        return dictionary_workbooks

    def no_publishing_feedback(self, local_logger):
        local_logger.debug(self.locale.gettext('No publishing action will take place!'))
        local_logger.debug(self.locale.gettext(
            'Check your input parameter values for accuracy and try again!'))

    def publish_data_source_to_tableau_server(self, local_logger, timer, publish_details):
        timer.start()
        local_logger.info(self.locale.gettext('About to start publishing'))
        data_source_name = Path(publish_details['Tableau Extract File'])\
            .name.replace('.hyper', '') + " Extract"
        project_data_source = tableauserverclient.DatasourceItem(
            publish_details['Project ID'], data_source_name)
        self.tableau_server.datasources.publish(
            project_data_source, publish_details['Tableau Extract File'],
            publish_details['Publishing Mode'])
        local_logger.info(self.locale.gettext('Publishing completed successfully!'))
        timer.stop()

    def clean_string(string):
        return (string or '').replace('\r\n', ' ').replace('\n', ' ').replace('\t', ' ')

    def store_fields_into_csv(self, field_name, data_source, workbook, worksheet='', seperator=','):
        return seperator.join([
            self.clean_string(data_source.caption or data_source.name),
            self.clean_string(os.path.basename(workbook.filename)),
            self.clean_string(worksheet),
            self.clean_string(field_name.caption),
            self.clean_string(field_name._aggregation),
            self.clean_string(field_name.alias),
            self.clean_string(field_name.calculation),
            self.clean_string(field_name.datatype),
            self.clean_string(field_name.description),
            self.clean_string(field_name.id),
            self.clean_string(field_name.role),
            self.clean_string(field_name._type),
        ]) + '\n'
