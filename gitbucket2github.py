#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests

GITBUCKET_API_BASEURL='http://gitbacket.example.com/api/v3/repos/USERNAME/REPONAME'
GITBUCKET_APP_TOKEN='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
GITBUCKET_MASTER_REPONAME='master'

GITHUB_API_BASEURL='https://api.github.com/repos/USERNAME/REPONAME'
GITHUB_APP_TOKEN='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
GITHUB_MASTER_REPONAME='main'
GITHUB_OWNERNAME='USERNAME'


# -- GitBacket ------------------------------------------------------------------------------------
# GitBucket ���� issue �� pull request ���擾����
# base_url (str) : ���|�W�g����URL
# token (str)    : �F�ؗp�g�[�N��
def get_issues (base_url, token):
    headers = {'Authorization': 'token ' + token}
    issues = []

    # issue
    for issue_type in ('issues', 'pulls'):
        url = '%s/%s' % (base_url, issue_type)
        for state in ('open', 'closed'):
            for page in range(1, 10000):
                payload = {'state': state, 'page':page}
                response = requests.get(url, headers=headers, params=payload)
                new_issues = response.json()
                if not len(new_issues):
                    break
                issues.extend(new_issues)
    issues.sort(key=lambda x: x['number'])

    # issue comment
    for issue in issues:
        response = requests.get(issue['comments_url'], headers=headers)
        issue['comments'] = response.json()

    return issues


# -- GitHub ---------------------------------------------------------------------------------------
# �N���[�Y�ς݂� Pull Request �̑���ƂȂ�_�~�[ issue ���쐬����
# base_url (str) : ���|�W�g����URL
# headers (dict) : �F�؏����i�[�������N�G�X�g�w�b�_
# title (str)    : �o�^����_�~�[ Issue �̃^�C�g��
# owner (str)    : �o�^����_�~�[ Issue �� assignee �ɓo�^���郆�[�U��
def create_dammy (base_url, headers, title, owner):

    # create a dammy issue.
    url = '%s/issues' % (base_url)
    labels = ['wontfix']
    assignees = [owner]
    body = 'This is a dummy issue instead of a closed pull request.'
    payload = json.dumps({'title':'[PULL] ' + title, 'body':body, 'labels': labels,
                          'assignees':assignees})
    response = requests.post(url, headers=headers, data=payload)

    # close the dammy issue.
    result = response.json()
    url = '%s/issues/%d' % (base_url, result['number'])
    payload = json.dumps({'state':'closed'})
    response = requests.post(url, headers=headers, data=payload)
    
    return


# Pull Request ���쐬����
# base_url (str)         : ���|�W�g����URL
# headers (dict)         : �F�؏����i�[�������N�G�X�g�w�b�_
# pull (dict)            : �o�^���� Pull Request
# gitbacket_master (str) : GitBacket�Ŏg���Ă��� master �u�����`�̖���
# github_master (str)    : GitHub�Ŏg���Ă��� master �u�����`�̖���
def create_pull (base_url, headers, pull, gitbacket_master, github_master):

    # Create a pull request.
    url = '%s/pulls' % (base_url)
    if issue['base']['ref'] == gitbacket_master:
        base = github_master
    else:
        base = issue['base']['ref']
    payload = json.dump({'title': issue['title'], 'body':issue['body'], 'head':issue['head']['ref'],
                         'base':base, 'draft':issue['draft']})
    response = requests.post(url, headers=headers, data=payload)
    pull_number = response.json()['number']

    # Create a pull comment.
    url = '%s/issues/%d/comments' % (base_url, issue_number)
    for comment in issue['comments']:
        payload = json.dumps({'body': comment['body']})
        response = requests.post(url, headers=headers, data=payload)

    # Close a pull.
    # �N���[�Y�ς݂� Pull Request �� �_�~�[ Issue �ɒu�������Ă���̂ő��݂��Ȃ�.
    return


# Issue ���쐬����
# base_url (str) : ���|�W�g����URL
# headers (dict) : �F�؏����i�[�������N�G�X�g�w�b�_
# issue (dict)   : �o�^���� Issue
# owner (list)   : assignees�Ɋ܂߂郆�[�U��.
def create_issue (base_url, headers, issue, owner):

    # Create an Issue.
    url = '%s/issues' % (base_url)
    # �S�Ẵ��[�U��GitHub�A�J�E���g��ɑ��݂���Ȃ� ...
    # assignees = [d.get('login') for d in issue['assignees']]
    assignees = [owner]
    labels = [d.get('name') for d in issue['labels']]
    payload = json.dumps({'title': issue['title'], 'body':issue['body'], 'labels': labels,
                          'assignees':assignees})
    response = requests.post(url, headers=headers, data=payload)
    issue_number = response.json()['number']

    # Create an issue comment.
    url = '%s/issues/%d/comments' % (base_url, issue_number)
    for comment in issue['comments']:
        payload = json.dumps({'body': comment['body']})
        response = requests.post(url, headers=headers, data=payload)
    
    # Close an issue.
    if issue['state'] == 'closed':
        url = '%s/issues/%d' % (base_url, issue_number)
        payload = json.dumps({'state': 'closed'})
        response = requests.post(url, headers=headers, data=payload)

    return


# GitHub �� issue �� pull request ��o�^����
# base_url (str)         : ���|�W�g����URL
# token (str)            : �F�ؗp�g�[�N��
# issues (list)          : get_issues�Ŏ擾���� issue
# gitbacket_master (str) : GitBacket�Ŏg���Ă��� master �u�����`�̖���
# github_master (str)    : GitHub�Ŏg���Ă��� master �u�����`�̖���
# owner (list)           : Pull Request �� assignees �Ɋ܂߂郆�[�U��
def put_issues (base_url, token, issues, gitbacket_master, github_master, owner):

    headers = {'Authorization': 'token ' + token}
    for issue in issues:
        # Pull Request �� Issue ���̔���
        if 'merged' in issue:
            if issue['state'] == 'closed':
                # �N���[�Y�ς� Pull Request �� �_�~�[ Issue �ɒu��������.
                create_dammy (base_url, headers, issue['title'], owner)
            else:
                # �I�[�v���� Pull Request �𓊍e����.
                create_pull (base_url, headers, issue, gitbacket_master, github_master)
        else:
            # Issue �𓊍e����.
            create_issue (base_url, headers, issue, owner)
    return


# main
if __name__ == '__main__':
    issues = get_issues(GITBUCKET_API_BASEURL, GITBUCKET_APP_TOKEN)
    put_issues(GITHUB_API_BASEURL, GITHUB_APP_TOKEN, issues, GITBUCKET_MASTER_REPONAME,
               GITHUB_MASTER_REPONAME, GITHUB_OWNERNAME)

