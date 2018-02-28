import os
import colored
import re
from colored import stylize
import requests
import subprocess

GH_CURR_USER = 'nickw444'
GH_ACCESS_TOKEN = os.environ['GH_ACCESS_TOKEN']


def make_pr(pull, with_author=False, with_number=True, with_reviews=False, with_branch=False):
    author = ''
    number = ''
    reviews = ''

    if with_author:
        author = '({}) '.format(stylize(pull['author']['login'], colored.fg('red')))

    if with_number:
        number = '({}) '.format(stylize('#{}'.format(pull['number']), colored.fg('green')))

    url = stylize(pull['url'], colored.fg('blue'))

    line = [
        ' - {title} {number}{author}'.format(number=number, title=pull['title'], author=author),
        '   {url} {reviews}'.format(url=url, reviews=reviews)
    ]
    if with_reviews:
        user_review_states = []

        for review in pull['reviews']['nodes']:
            user_review_states.append((review['author']['login'], review['state']))

        for request in pull['reviewRequests']['nodes']:
            user_review_states.append((request['requestedReviewer']['login'], 'REQUESTED'))

        user_states = {}
        for (user, state) in reversed(user_review_states):
            if user == GH_CURR_USER:
                continue

            if user in user_states and user_states[user] != 'COMMENTED':
                continue

            user_states[user] = state

        approvals = [k for (k, v) in user_states.items() if v == 'APPROVED']
        pending = [k for (k, v) in user_states.items() if v != 'APPROVED']
        changes_required = 'CHANGES_REQUESTED' in user_states.values()

        components = []
        if (len(approvals)):
            components.append('{} approvals ({})'.format(len(approvals), ', '.join(approvals)))
        if (len(pending)):
            components.append('{} pending ({})'.format(len(pending), ', '.join(pending)))
        if changes_required:
            components.append('changes required')

        style = None
        components_str = ', '.join(components)
        if len(pending) == 0:
            components_str += ' 🎉'
            style = colored.fg('green') + colored.attr('bold')
        elif changes_required:
            components_str += ' 😭'
            style = colored.fg('red') + colored.attr('bold')
        else:
            style = colored.attr('dim')

        components_str = stylize(components_str, style)
        line.insert(1, '   {}'.format(components_str))

    if with_branch:
        line.append('   {}'.format(stylize(pull['headRefName'], colored.fg('blue') + colored.attr('dim'))))

    return '\n'.join(line)


def make_title(emoji, text):
    return '{}  '.format(emoji) + stylize(text, colored.fg('white') + colored.attr('underlined')) + '\n'


def check_pending_reviews(data):
    pull_requests = data['reviewRequests']['nodes']
    if len(pull_requests) > 0:
        print(make_title('👋', 'You have pending review requests ({})'.format(len(pull_requests))))
        for pull in pull_requests:
            print(make_pr(pull, with_author=True))

    print("")


def check_open_prs(data, repo_namespace):
    pull_requests = data['user']['openPRs']['nodes']
    pull_requests = list(filter(lambda req: repo_namespace in req['url'], pull_requests))
    if len(pull_requests) > 0:
        print(make_title('😡', 'Your open pull requests for this repo ({})'.format(len(pull_requests))))
        for pull in pull_requests:
            print(make_pr(pull, with_reviews=True, with_author=False, with_branch=True))
            print("")
    print("")


def check_current_branch(data, repo_url, current_branch, base_branch='master'):
    print(make_title('🤑', 'Branch Pull Requests:'))
    pull_requests = data['user']['branchPR']['nodes']
    if len(pull_requests) > 0:
        for pull in pull_requests:
            print(make_pr(pull))
    else:
        compare_link = '{}/compare/{}...{}'.format(repo_url, base_branch, current_branch)
        compare_link = stylize(compare_link, colored.fg('blue'))

        print(
            '   No pull requests were found for this branch. {}:\n'.format(stylize('Create one', colored.attr('bold'))))
        print('   {}'.format(compare_link))

    print("")


def make_request(user, head_ref):
    query = open(os.path.join(os.path.dirname(__file__), 'query.txt')).read()
    query = query.replace('{username}', user)
    query = query.replace('{branchname}', head_ref)

    resp = requests.post('https://api.github.com/graphql',
                         headers={
                             'Authorization': 'bearer {}'.format(GH_ACCESS_TOKEN)
                         },
                         json={'query': query})

    if not resp.ok:
        raise Exception("Request failed ({}): {}".format(resp.status_code, resp.text))

    return resp.json()


def get_repo_current_branch():
    return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('UTF-8').strip()


namespace_re = re.compile(r'(.*)\.git')


def get_repo_namespace():
    origin = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('UTF-8').strip()
    domain, path = origin.split(':')
    result = namespace_re.match(path)
    return result.group(1)


def main():
    current_branch = get_repo_current_branch()
    repo_namespace = get_repo_namespace()

    response = make_request(GH_CURR_USER, current_branch)
    data = response['data']
    check_open_prs(data, repo_namespace)
    check_pending_reviews(data)
    check_current_branch(data, 'https://github.com/{}'.format(repo_namespace), current_branch=current_branch)


main()
