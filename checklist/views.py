from django.shortcuts import render, reverse
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.views.generic.detail import BaseDetailView
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from tournament.models import Tournament
from tournament.views import TabsViewMixin, get_toolbox, get_tabs
from checklist.models import *

PROGRESS_BAR_COLOR = {
    '1_pre_reg': 'success',
    '2_pre_tour': 'info',
    '3_on_place': 'warning',
    '4_post_tour': 'danger',
}


class ChecklistDetailView(DetailView):
    template_name = 'checklist/checklist.html'

    model = Tournament
    context_object_name = 'tournament'

    def get(self, *args, **kwargs):
        t = self.get_object()
        if len(Checklist.objects.filter(tournament=t)) == 1:
            return super(ChecklistDetailView, self).get(*args, **kwargs)
        else:
            return redirect('admin:checklist_checklist_changelist')

    def get_context_data(self, **kwargs):
        context = super(ChecklistDetailView, self).get_context_data(**kwargs)
        t = self.get_object()

        checklist = []
        phase_list = []
        for p in PHASES:
            tasks = Task.objects.filter(phase=p[0])
            todo = TaskStatus.objects.filter(
                checklist=t.checklist,
                done=False,
                task__in=tasks,
            )
            done = TaskStatus.objects.filter(
                checklist=t.checklist,
                done=True,
                task__in=tasks,
            )
            if len(todo)+len(done) == 0:
                phase = (
                    PROGRESS_BAR_COLOR[p[0]],
                    25,
                    100,
                )
            else:
                phase = (
                    PROGRESS_BAR_COLOR[p[0]],
                    int(round((100*len(done)/(len(todo)+len(done)))/4, 0)),
                    int(round(100*len(done)/(len(todo)+len(done)), 0)),
                )

            phase_list.append(phase)
            checklist.append((
                (p[1], PROGRESS_BAR_COLOR[p[0]]),
                todo,
                done
            ))

        context.update({
            'tabs': get_tabs(self.request, t),
            'toolbox': get_toolbox(self.request.user, t),
            'checklist': checklist,
            'phases': phase_list,
        })

        return context


class JSONResponseMixin:

    def render_to_json_response(self, context, pk=None, **response_kwargs):
        response = JsonResponse(
            self.get_data(context),
            **response_kwargs,
            safe=False
        )

        return response

    def get_data(self, context):
        data = [
            context['phase_update'],
        ]

        return list(data)


class ChangeTaskAjaxView(JSONResponseMixin, BaseDetailView):
    model = Tournament

    def get(self, request, *args, **kwargs):
        tournament = self.get_object()
        task_pk = self.request.GET.get('task', None)
        try:
            task = TaskStatus.objects.get(pk=task_pk)
        except(task.DoesNotExist):
            raise Http404('Táto úloha neexistuje')

        if task.checklist.tournament.pk != tournament.pk:
            raise PermissionDenied()

        if request.user.is_staff:
            task.done = not task.done
            task.save()

        phase_list = []
        for p in PHASES:
            tasks = Task.objects.filter(phase=p[0])
            todo = len(TaskStatus.objects.filter(
                checklist=task.checklist,
                done=False,
                task__in=tasks,
            ))
            done = len(TaskStatus.objects.filter(
                checklist=task.checklist,
                done=True,
                task__in=tasks,
            ))
            if todo + done == 0:
                phase = (
                    25,
                    100,
                )
            else:
                phase = (
                    int(round((100*done/(todo+done))/4, 0)),
                    int(round(100*done/(todo+done), 0)),
                )
            phase_list.append(phase)

        context = {
            'phase_update': phase_list,
        }

        return self.render_to_json_response(context, **kwargs)
