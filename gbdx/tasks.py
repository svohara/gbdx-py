'''
Created on Aug 13, 2015
@author: sohara

Functions to interface with tasks and workflows
'''
import json
import sys

from gbdx import GBDX_BASE_URL, GBDX_WORKFLOW_STATES, get_json, post_json

def list_available_tasks(sess):
    """
    lists the available tasks on the gbdx platform
    """
    url = "/".join([GBDX_BASE_URL,'workflows','v1','tasks'])
    ret = get_json(sess, url)
    return ret["tasks"]

def get_task_definition(sess, task_name):
    """
    Gets the definition of a task
    @param sess: The gbdx session object
    @param task_name: The identifier of the task, such as FastOrtho,
    such as is returned by list_available_tasks 
    """
    url = "/".join([GBDX_BASE_URL,'workflows','v1','tasks',task_name])
    return get_json(sess, url)

def summarize_workflow_tasks(workflow_dict):
    task_summary = []
    tasks = workflow_dict["tasks"]
    for t in tasks:
        name = t['name']
        task_type = t['taskType']
        task_state = t['state']['state']
        task_summary.append("\t{0}({1}):{2}".format(name,task_type,task_state))
    return "\n".join(task_summary)

def search_workflows(sess, state="all", owner=None, lookback_h=3, details=False, verbose=False):
    """
    Lists the workflows that are in a given state
    @param sess: The gbdx session object
    @param state: The state of the workflow. Must be one of the
    values defined by GBDX_WORKFLOW_STATES
    @param owner: If provided, will filter by the owner's id, otherwise
    will show the results for any owner.
    @param lookback_h: The number of hours from now to constrain
    the search. Default is 3, so you can list all the workflows in
    a given state within the past 3 hours.
    @param details: If True, this function will also retrieve summary details
    for each of the workflows that match the filter. If False, only the workflow
    ids will be returned. This will be slow if there are many workflows.
    @param verbose: If True and details is also true, then as the workflow details
    are returned, they are printed to standard out.
    @return: (workflow_ids, summary), where workflow_ids is a list of workflow ids,
    and summary contains the summary information, only if details=True, else None.
    """
    state = state.lower()
    assert state in GBDX_WORKFLOW_STATES
    url = "/".join([GBDX_BASE_URL,'workflows','v1','workflows','search'])
    search_filter = {"state":state, "lookback_h":lookback_h}
    if owner:
        search_filter["owner"]=owner
    payload = json.dumps(search_filter)
    ret = post_json(sess, url, payload)
    workflow_ids = ret['Workflows']
    summary = None
    if details:
        summary = ""
        for wf_id in workflow_ids:
            tmp = get_workflow_status(sess, wf_id)
            this_task = "Workflow {id} ({owner})\n".format(**tmp)
            this_task += summarize_workflow_tasks(tmp)
            this_task += "\n"
            if verbose: 
                print this_task,  #incrementally print results
                sys.stdout.flush()
            summary += this_task
        print ""
    return (workflow_ids, summary)

def get_workflow_status(sess, workflow_id):
    """
    retrieves the status for a given workflow
    @param sess: The gbdx session object
    @param workflow_id: The workflow id
    """
    url = "/".join([GBDX_BASE_URL,'workflows','v1','workflows',workflow_id])
    return get_json(sess, url)

if __name__ == '__main__':
    pass