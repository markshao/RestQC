fail_cases_by_project = {}

def update_fail_cases(testset_id,data,**kwargs):
    global fail_cases_by_project
    fail_cases_by_project[testset_id] = data