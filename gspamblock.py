from __future__ import print_function
import pickle
import os.path
import pprint
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError 


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.settings.basic']

def get_junk_labels(service):
    # get ID of 'Junk' label
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    junk_labels = [l['id'] for l in labels if l['name'] == 'Junk']
    return junk_labels

def add_filter(service, from_):
    add_label_ids = get_junk_labels(service)

    filter = {
        'action': {
            'removeLabelIds': ['UNREAD', 'INBOX'],
            'addLabelIds': add_label_ids, # Junk label
        }, 
        'criteria': {'from': from_}
    }

    try:
        result = service.users().settings().filters().create(userId='me', body=filter).execute()
        print('Created filter:')
        pprint.pprint(result)
    except HttpError as http_error:
        if 'Filter already exists' in str(http_error):
            print('Filter already exists: ' + from_)
        else:
            raise http_error


def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    parser = argparse.ArgumentParser(description='Manage GMail Filters for junk blocking')
    parser.add_argument('-l', '--list', help='list filters', action='store_true')
    parser.add_argument('-a', '--address', metavar='ADDRESS', help='add filter for email ADDRESS')
    parser.add_argument('-d', '--domain', metavar='DOMAIN', help='add filter for DOMAIN (strip name from email address)')
    parser.add_argument('-r', '--remove', metavar='ID', help='remove filter with id ID')
    parser.add_argument('--labels', help='list all labels', action='store_true')
    parser.add_argument('--listnospam', help='list all rules which are not set up to block spam', action='store_true')
    parser.add_argument('--listsimilarfrom', help='list all rules with similar from', action='store_true')
    args = parser.parse_args()

    if args.list:
        result = service.users().settings().filters().list(userId='me').execute()
        filters = result.get('filter', [])
        print('Existing filters:')
        pprint.pprint(filters)
        print(len(filters), 'filters')

    if args.listsimilarfrom:
        result = service.users().settings().filters().list(userId='me').execute()
        filters = result.get('filter', [])
        for f1 in filters:
            from1 = f1.get('criteria', []).get('from', [])
            if not from1:
                continue
            for f2 in filters:
                from2 = f2.get('criteria', []).get('from', [])
                if not from2:
                    continue
                if f1['id'] == f2['id']:
                    continue
                if from1 in from2:
                    print()
                    if from1 == from2:
                        print("Same:", repr(from1), repr(from2))
                    else:
                        print("Similar:", repr(from1), repr(from2))
                    pprint.pprint(f1)
                    pprint.pprint(f2)

    if args.listnospam:
        result = service.users().settings().filters().list(userId='me').execute()
        filters = result.get('filter', [])
        junk_labels = get_junk_labels(service)
        nospam_filters = []
        for f in filters:
            if f['action']['removeLabelIds'] == ['UNREAD', 'INBOX'] and f['action']['addLabelIds'] == junk_labels:
                continue
            nospam_filters.append(f)
        print('Existing non-spam filters:')
        pprint.pprint(nospam_filters)

    if args.address:
        add_filter(service, args.address)

    if args.domain:
        if '@' in args.domain:
            domain = args.domain.split('@', 1)[1] # extract the domain name
        add_filter(service, domain)

    if args.remove:
        result = service.users().settings().filters().delete(userId='me', id=args.remove).execute()
        print('Removed filter')
        pprint.pprint(result)

    if args.labels:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            pprint.pprint(labels)
            print(len(labels), 'labels')

if __name__ == '__main__':
    main()

