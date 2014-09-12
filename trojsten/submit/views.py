# -*- coding: utf-8 -*-
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf import settings
from trojsten.regal.contests.models import Round
from trojsten.regal.tasks.models import Task, Submit
from trojsten.submit.forms import SourceSubmitForm, DescriptionSubmitForm
from trojsten.submit.helpers import save_file, process_submit, get_path,\
    update_submit
from sendfile import sendfile
import os
import xml.etree.ElementTree as ET


@login_required
def view_submit(request, submit_id):
    submit = get_object_or_404(Submit, pk=submit_id)
    if submit.user != request.user:
        raise PermissionDenied()  # You shouldn't see other user's submits.

    # For source submits, display testing results, source code and submit list.
    if submit.submit_type == Submit.SOURCE:
        if submit.testing_status == 'in queue':
            # check if submit wasn't tested yet
            update_submit(submit)
        template_data = {'submit': submit}
        protocol_path = submit.filepath.rsplit(
            '.', 1)[0] + settings.PROTOCOL_FILE_EXTENSION
        if os.path.exists(protocol_path):
            template_data['protocolReady'] = True  # Tested, show the protocol
            tree = ET.parse(protocol_path)  # Protocol is in XML format
            clog = tree.find("compileLog")
            # Show compilation log if present
            template_data['compileLogPresent'] = clog is not None
            if clog is None:
                clog = ""
            else:
                clog = clog.text
            template_data['compileLog'] = clog
            tests = []
            runlog = tree.find("runLog")
            if runlog is not None:
                for runtest in runlog:
                    # Test log format in protocol is:
                    # name, resultCode, resultMsg, time, details
                    if runtest.tag != 'test':
                        continue
                    test = {}
                    test['name'] = runtest[0].text
                    test['result'] = runtest[2].text
                    test['time'] = runtest[3].text
                    if len(runtest) > 4:
                        details = runtest[4].text
                    else:
                        details = None
                    test['details'] = details
                    showDetails = details is not None and 'sample' in test['name']
                    test['showDetails'] = showDetails
                    tests.append(test)
            template_data['tests'] = tests
            template_data['have_tests'] = len(tests) > 0
        else:
            template_data['protocolReady'] = False  # Not tested yet!
        if os.path.exists(submit.filepath):
            # Source code available, display it!
            template_data['fileReady'] = True
            with open(submit.filepath, "r") as submitfile:
                data = submitfile.read()
                template_data['data'] = data
        else:
            template_data['fileReady'] = False  # File does not exist on server
        return render(
            request, 'trojsten/submit/view_submit.html', template_data
        )

    # For description submits, return submitted file.
    if submit.submit_type == Submit.DESCRIPTION:
        if os.path.exists(submit.filepath):
            return sendfile(
                request,
                submit.filepath,
            )
        else:
            raise Http404  # File does not exists, can't be returned


@login_required
def task_submit_page(request, task_id):
    '''View, ktory zobrazi formular na odovzdanie a zoznam submitov
    prave prihlaseneho cloveka pre danu ulohu'''
    task = get_object_or_404(Task, pk=task_id)
    template_data = {'task': task}
    return render(request, 'trojsten/submit/task_submit.html', template_data)


@login_required
def round_submit_page(request, round_id):
    '''View, ktorý zobrazí formuláre pre odovzdanie pre všetky úlohy
    z daného kola'''
    round = get_object_or_404(Round, pk=round_id)
    tasks = Task.objects.filter(round=round).order_by('number')
    template_data = {'round': round, 'tasks': tasks}
    return render(request, 'trojsten/submit/round_submit.html', template_data)


@login_required
def task_submit_post(request, task_id, submit_type):
    '''Spracovanie uploadnuteho submitu'''
    try:
        submit_type = int(submit_type)
    except ValueError:
        raise HttpResponseBadRequest

    # Raise Not Found when submitting non existent task
    task = get_object_or_404(Task, pk=task_id)

    # Raise Not Found when submitting non-submittable submit type
    if not task.has_submit_type(submit_type):
        raise Http404

    # Raise Not Found when not submitting through POST
    if request.method != "POST":
        raise Http404

    sfile = request.FILES['submit_file']

    if submit_type == Submit.SOURCE:
        form = SourceSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            language = form.cleaned_data['language']
            # Source submit's should be processed by process_submit()
            submit_id = process_submit(sfile, task, language, request.user)
            # Source file-name is id.data
            sfiletarget = os.path.join(get_path(
                task, request.user), submit_id + '.data')
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         user=request.user,
                         submit_type=submit_type,
                         points=0,
                         filepath=sfiletarget,
                         testing_status='in queue',
                         protocol_id=submit_id)
            sub.save()
            if 'redirect_to' in request.POST:
                return redirect(request.POST['redirect_to'])
            else:
                return redirect(
                    reverse(
                        'task_submit_page', kwargs={'task_id': int(task_id)}
                    )
                )

    elif submit_type == Submit.DESCRIPTION:
        form = DescriptionSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            # Description submit id's are currently timestamps
            from time import time
            submit_id = str(int(time()))
            # Description file-name should be: surname-id-originalfilename
            sfiletarget = os.path.join(
                get_path(task, request.user),
                "%s-%s-%s" % (request.user.last_name, submit_id, sfile.name),
            )
            save_file(sfile, sfiletarget)
            sub = Submit(task=task,
                         user=request.user,
                         submit_type=submit_type,
                         points=0,
                         testing_status='in queue',
                         filepath=sfiletarget)
            sub.save()
            if 'redirect_to' in request.POST:
                return redirect(request.POST['redirect_to'])
            else:
                return redirect(
                    reverse(
                        'task_submit_page', kwargs={'task_id': int(task_id)}
                    )
                )

    else:
        # Only Description and Source submitting is developed currently
        raise Http404
